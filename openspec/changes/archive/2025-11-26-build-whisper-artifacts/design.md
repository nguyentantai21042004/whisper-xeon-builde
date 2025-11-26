# Design: Automated Whisper Artifact Build System

## Context

The whisper.cpp project provides high-performance ASR inference with support for various hardware accelerators. For Intel Xeon deployments, we need:
- Optimized shared library compilation with AVX2/AVX512 and optional OpenBLAS
- Automated model quantization to q5_1 format for memory efficiency
- Self-contained packaging for easy deployment to production environments
- MinIO integration for centralized artifact distribution

**Constraints:**
- Must maintain whisper.cpp's zero-dependency philosophy for core library
- Build environment must be reproducible across different systems
- Package structure must support independent deployment of different model sizes
- Must work within Linux Intel Xeon environments with AVX2/AVX512 support

**Stakeholders:**
- DevOps engineers deploying whisper models to production
- Python application developers integrating whisper via ctypes
- Infrastructure teams managing model artifact storage

## Goals / Non-Goals

**Goals:**
- Automate complete build-to-package pipeline using Docker multi-stage builds
- Generate self-contained directories (library + model) for Small and Medium models
- Provide ready-to-use Python integration examples in documentation
- Enable automated upload to MinIO storage
- Support AVX2/FMA optimizations for Intel Xeon processors

**Non-Goals:**
- Supporting models other than Small and Medium (can be added later)
- GPU acceleration (CUDA, OpenVINO) in initial implementation
- Windows or ARM build targets
- Custom quantization formats beyond q5_1
- Python package/wheel distribution (ctypes loading only)

## Decisions

### Decision 1: Docker Multi-Stage Build

**Choice:** Use Docker multi-stage build with 3 stages: Builder, Organizer, Output

**Rationale:**
- **Reproducibility:** Ensures consistent build environment regardless of host system
- **Isolation:** Clean build without host system dependencies
- **Efficiency:** Multi-stage design separates build artifacts from final output
- **CI/CD Ready:** Easy integration with containerized pipelines

**Alternatives considered:**
- Shell scripts on host: Rejected due to dependency management complexity
- Single-stage Docker: Rejected due to larger image size and mixed concerns
- VM-based builds: Rejected due to overhead and slower iteration

### Decision 2: Artifact Directory Structure

**Choice:** Independent directories per model with duplicated `libwhisper.so`

```
/release_artifacts
├── whisper_small_xeon/
│   ├── libwhisper.so
│   └── ggml-small-q5_1.bin
└── whisper_medium_xeon/
    ├── libwhisper.so
    └── ggml-medium-q5_1.bin
```

**Rationale:**
- **Independence:** Each directory is self-contained and deployable alone
- **Simplicity:** No shared dependencies or path resolution complexity
- **Robustness:** Copying entire folder guarantees functionality
- **Disk trade-off:** Small library duplication (~few MB) vs deployment safety

**Alternatives considered:**
- Shared library with symlinks: Rejected due to deployment complexity
- Flat structure: Rejected due to lack of logical organization
- Separate lib/ and models/ directories: Rejected due to lost independence

### Decision 3: Quantization Format

**Choice:** Use q5_1 quantization for all models

**Rationale:**
- **Balance:** Good trade-off between model size and accuracy
- **Compatibility:** Well-tested format in whisper.cpp ecosystem
- **Performance:** Efficient on Xeon CPUs with AVX2
- **Existing tooling:** Supported by examples/quantize

**Alternatives considered:**
- q8_0: Rejected due to larger size with marginal accuracy gain
- q4_0: Rejected due to potential accuracy degradation
- Mixed formats: Rejected to maintain consistency

### Decision 4: Shell Script for MinIO Upload

**Choice:** Provide `push_to_minio.sh` shell script using `mc` or `aws s3` CLI

**Rationale:**
- **Environment agnostic:** Works in Docker, CI/CD, and manual workflows
- **No Python dependency:** Keeps automation lightweight
- **Standard tools:** MinIO CLI tools widely available
- **Flexibility:** Easy to customize for different storage backends

**Alternatives considered:**
- Python script: Rejected to avoid additional dependencies
- Integrated into Dockerfile: Rejected to separate concerns (build vs deploy)
- Manual upload: Rejected due to automation goals

### Decision 5: CMake Build with Specific Flags

**Choice:** Use CMake with `-DGGML_AVX2=ON -DGGML_FMA=ON -DBUILD_SHARED_LIBS=ON`

**Rationale:**
- **Optimization:** AVX2 and FMA enable Xeon-specific SIMD optimizations
- **Shared library:** Required for Python ctypes integration
- **Project alignment:** Follows whisper.cpp's build system conventions
- **Optional OpenBLAS:** Can be added via `-DGGML_BLAS=ON` for BLAS acceleration

**Alternatives considered:**
- Makefile: Rejected due to less flexible cross-platform configuration
- Static library: Rejected as it doesn't meet Python ctypes requirements
- AVX512: Not enabled by default to maintain broader Xeon compatibility

## Technical Architecture

### Build Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: Builder                                            │
│ - Install build dependencies (cmake, gcc, wget)             │
│ - Clone/copy whisper.cpp source                             │
│ - CMake configure with AVX2/FMA flags                       │
│ - Build libwhisper.so                                       │
│ - Build quantize tool                                       │
│ - Download Small and Medium base models                     │
│ - Quantize models to q5_1 format                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 2: Organizer                                          │
│ - Create /release_artifacts structure                       │
│ - Copy libwhisper.so to each model directory                │
│ - Copy quantized .bin files to respective directories       │
│ - Generate README.md with Python examples                   │
│ - Create push_to_minio.sh script                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Stage 3: Output                                             │
│ - Final minimal image with /release_artifacts               │
│ - Or: Volume mount to extract to host filesystem            │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Workflow

1. **Build:** `docker build -t whisper-builder .`
2. **Extract:** `docker run -v $(pwd)/artifacts:/output whisper-builder cp -r /release_artifacts /output/`
3. **Deploy:**
   - Copy `whisper_small_xeon/` or `whisper_medium_xeon/` to production server
   - Set `LD_LIBRARY_PATH` or load via Python ctypes with explicit path
4. **Upload:** Run `bash push_to_minio.sh` to sync to storage

### Python Integration Example

```python
import ctypes
import os

# Load library from package directory
lib_path = "/path/to/whisper_small_xeon/libwhisper.so"
model_path = "/path/to/whisper_small_xeon/ggml-small-q5_1.bin"

whisper = ctypes.CDLL(lib_path)
ctx = whisper.whisper_init_from_file(model_path.encode('utf-8'))
```

## Risks / Trade-offs

### Risk 1: Library ABI Compatibility
**Risk:** `libwhisper.so` built in Docker may not work on all Xeon variants
**Mitigation:**
- Use common base image (Ubuntu LTS or CentOS)
- Document minimum glibc version requirements
- Provide build script for local compilation if needed

### Risk 2: Model Download Failures
**Risk:** Hugging Face or model source may be unavailable during build
**Mitigation:**
- Add retry logic to download scripts
- Support local model file input as alternative
- Cache models in Docker layers when possible

### Risk 3: Disk Space Usage
**Risk:** Large model files and Docker layers consume significant space
**Mitigation:**
- Use `.dockerignore` to exclude unnecessary files
- Multi-stage build minimizes final image size
- Document disk requirements (estimate ~4GB per model)

### Trade-off 1: Library Duplication
**Trade-off:** Each model directory contains copy of libwhisper.so (~2-5MB)
**Decision:** Accept duplication for deployment independence
**Impact:** ~10MB total overhead vs simplified deployment

### Trade-off 2: Quantization Quality
**Trade-off:** q5_1 format reduces accuracy slightly vs fp16/fp32
**Decision:** Accept minor quality loss for 4-8x size reduction
**Impact:** Typically <1% WER increase, acceptable for production

## Migration Plan

This is a new capability, no migration needed.

**Rollout steps:**
1. Implement and test Dockerfile locally
2. Validate artifact generation with Small model
3. Extend to Medium model
4. Test Python integration with sample audio
5. Validate MinIO upload script
6. Document usage and requirements

**Rollback:**
Not applicable - this is additive tooling that doesn't affect existing build systems.

## Open Questions

1. **Should we support custom quantization levels?**
   - Current: Fixed q5_1 format
   - Consideration: Allow q4_0, q8_0 via build arguments
   - Decision: Defer to future iteration based on user feedback

2. **Should we pre-generate Python wheels?**
   - Current: Raw ctypes integration
   - Consideration: Package as pip-installable wheel
   - Decision: Out of scope - ctypes approach maintains flexibility

3. **Should we support incremental builds?**
   - Current: Full rebuild each time
   - Consideration: Cache compiled objects between runs
   - Decision: Docker layer caching provides sufficient optimization

4. **What MinIO configuration should be documented?**
   - Current: Generic mc/aws s3 examples
   - Consideration: Specific bucket structure recommendations
   - Decision: Provide template script, let users customize for their environment
