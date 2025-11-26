# Whisper Xeon Builder

A specialized build pipeline for creating Intel Xeon-optimized Whisper artifacts with AVX2 and FMA optimizations.

## Project Goal

This repository is a focused fork of [whisper.cpp](https://github.com/ggml-org/whisper.cpp) designed specifically to:

1. Build Whisper libraries optimized for Intel Xeon processors
2. Generate quantized models for efficient inference
3. Package artifacts for easy deployment
4. Upload to MinIO for distribution

## Pipeline Overview

```
Source Code → Docker Build → Optimized Artifacts → MinIO Storage
```

### Pipeline Stages

1. **Build Stage**: Compiles `libwhisper.so` and dependencies with Xeon-specific optimizations (AVX2/FMA)
2. **Model Stage**: Downloads and quantizes Whisper models (small, medium) to Q5_1 format
3. **Package Stage**: Organizes artifacts into deployment-ready modules
4. **Distribution Stage**: Uploads to MinIO object storage

## Quick Start

### Building Artifacts

```bash
# Build Docker image and generate artifacts
docker build -t whisper-xeon-builder .

# Extract artifacts from the container
docker create --name whisper-temp whisper-xeon-builder
docker cp whisper-temp:/release_artifacts/. ./artifacts/
docker rm whisper-temp
```

Or use this one-liner:

```bash
docker build -t whisper-xeon-builder . && \
  docker create --name whisper-temp whisper-xeon-builder && \
  docker cp whisper-temp:/release_artifacts/. ./artifacts/ && \
  docker rm whisper-temp
```

### Artifact Structure

After building, you'll find the following structure:

```
artifacts/
├── whisper_small_xeon/
│   ├── libwhisper.so          # Main whisper library
│   ├── libggml.so.0           # GGML computation library
│   ├── libggml-base.so.0      # GGML base library
│   ├── libggml-cpu.so.0       # GGML CPU backend
│   ├── ggml-small-q5_1.bin    # Quantized small model
│   └── README.md              # Usage instructions
│
├── whisper_medium_xeon/
│   ├── libwhisper.so
│   ├── libggml.so.0
│   ├── libggml-base.so.0
│   ├── libggml-cpu.so.0
│   ├── ggml-medium-q5_1.bin   # Quantized medium model
│   └── README.md
│
└── push_to_minio.sh           # MinIO upload script
```

## Using the Artifacts

### Python Integration

```python
import ctypes
import os

# Load the library
lib_path = "./whisper_small_xeon/libwhisper.so"
lib = ctypes.CDLL(lib_path)

# Initialize Whisper with model
model_path = "./whisper_small_xeon/ggml-small-q5_1.bin"
ctx = lib.whisper_init_from_file(model_path.encode('utf-8'))

# Use for transcription
# ... (see full API in include/whisper.h)
```

### C/C++ Integration

```cpp
#include "whisper.h"

int main() {
    // Initialize
    struct whisper_context* ctx = whisper_init_from_file(
        "whisper_small_xeon/ggml-small-q5_1.bin"
    );
    
    // Use for transcription
    // ...
    
    whisper_free(ctx);
    return 0;
}
```

Link with: `-lwhisper -lggml -lggml-base -lpthread -lm`

## MinIO Upload

Upload artifacts to MinIO object storage using curl (no need to install mc client):

```bash
cd artifacts/

# Configure and upload (default: localhost MinIO)
export MINIO_IP=127.0.0.1
export MINIO_PORT=9000
export MINIO_ACCESS_KEY=minioadmin
export MINIO_SECRET_KEY=minioadmin
export BUCKET=whisper-artifacts

./push_to_minio.sh
```

The script uses MinIO's S3-compatible API via curl, so you only need `curl` installed (usually pre-installed on most systems).

**Requirements:**
- `curl` command (check: `which curl`)
- MinIO server accessible at specified IP:PORT
- Valid access key and secret key

**Alternative: Using mc client** (if you prefer):

```bash
# Install MinIO client
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/

# Configure and upload
mc alias set myminio http://your-minio-ip:9000 ACCESS_KEY SECRET_KEY
mc cp --recursive whisper_small_xeon/ myminio/whisper-artifacts/whisper_small_xeon/
mc cp --recursive whisper_medium_xeon/ myminio/whisper-artifacts/whisper_medium_xeon/
```

## System Requirements

### Build Requirements

- Docker (for containerized build)
- 4GB+ RAM
- 10GB+ disk space

### Runtime Requirements

- Linux x86_64
- CPU with AVX2 and FMA support (Intel Xeon, Core i5/i7/i9 4th gen+)
- `libgomp1` (OpenMP runtime): `apt-get install libgomp1`

Check CPU support:

```bash
grep -E "avx2|fma" /proc/cpuinfo
```

## Build Optimizations

This build includes the following Xeon-specific optimizations:

- **AVX2**: 256-bit SIMD instructions for parallel processing
- **FMA**: Fused multiply-add for faster matrix operations
- **Shared Libraries**: Smaller binary size and easier updates
- **Q5_1 Quantization**: 5-bit quantization with reduced memory footprint

## Model Information

### Small Model
- Parameters: ~244M
- Memory: ~466 MB (quantized)
- Best for: Fast transcription, lower accuracy requirements

### Medium Model
- Parameters: ~769M  
- Memory: ~1.5 GB (quantized)
- Best for: Higher accuracy, acceptable speed trade-off

## Repository Structure

This is a pruned repository containing only essential build components:

```
whisper-xeon-builder/
├── Dockerfile              # Multi-stage build definition
├── CMakeLists.txt         # Build configuration
├── src/                   # Whisper source code
├── ggml/                  # GGML library source
├── include/               # Public headers
├── examples/quantize/     # Model quantization tool
├── models/                # Model download scripts
├── artifacts/             # Build outputs (gitignored)
└── scripts/               # Build utilities
```

## Troubleshooting

### Library Not Found Error

```bash
# Set LD_LIBRARY_PATH to include library location
export LD_LIBRARY_PATH=/path/to/whisper_small_xeon:$LD_LIBRARY_PATH
```

### AVX2/FMA Not Supported

If your CPU doesn't support AVX2/FMA, rebuild without these flags (performance will be reduced):

```dockerfile
# Modify Dockerfile line 27-30:
RUN cmake -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=ON \
    ...
```

### Docker Build Fails

Ensure you have sufficient disk space and memory:

```bash
docker system prune -a  # Clean up Docker
docker build --no-cache -t whisper-xeon-builder .
```

## Documentation

- [Build Artifacts Usage](BUILD_ARTIFACTS_USAGE.md) - Detailed usage instructions
- [Whisper API Reference](include/whisper.h) - C API documentation
- [Original whisper.cpp](README.original.md) - Full upstream documentation

## Testing

**Note**: The built artifacts are Linux binaries and must be tested on Linux (or in a Linux container).

Test on Linux:

```bash
python3 test_artifacts.py
```

Test in Docker container (from macOS/Windows):

```bash
docker run --rm \
  -v $(pwd)/artifacts:/artifacts \
  -v $(pwd)/test_artifacts.py:/test_artifacts.py \
  ubuntu:22.04 \
  bash -c "apt-get update -qq && apt-get install -y -qq python3 libgomp1 > /dev/null && python3 /test_artifacts.py"
```

## Contributing

This repository focuses on Xeon build optimization. For general Whisper features, contribute to the upstream project.

For build-specific issues:
1. Check Docker build logs
2. Verify CPU compatibility
3. Test with `test_artifacts.py`
4. Open an issue with logs and system info

## Credits

- Original whisper.cpp: [ggml-org](https://github.com/ggml-org/whisper.cpp)
- OpenAI Whisper: [openai/whisper](https://github.com/openai/whisper)
- GGML: [ggml-org/ggml](https://github.com/ggml-org/ggml)
