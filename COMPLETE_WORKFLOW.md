# Complete Workflow - Whisper Xeon Builder

## Overview
This document provides the complete workflow from repository pruning to artifact deployment.

## Step 1: Repository Pruning (Optional but Recommended)

### Preview Changes
```bash
python3 maintenance_prune.py --dry-run
```

This will show:
- ✅ ~1115 files/directories kept
- ❌ ~78 items removed (bindings/, tests/, samples/, extra examples/)
- ✅ `bindings/javascript/package-tmpl.json` **IS KEPT** (required for build)

### Execute Pruning
```bash
python3 maintenance_prune.py
# Type 'yes' when prompted to confirm
```

## Step 2: Build Docker Image

```bash
docker build -t whisper-xeon-builder .
```

**Build time:** 15-30 minutes (first time), 5-10 minutes (cached)

**What happens:**
1. Builds `libwhisper.so` with AVX2/FMA optimizations
2. Builds quantize tool manually
3. Downloads Whisper Small and Medium models
4. Quantizes models to q5_1 format
5. Packages everything in `/release_artifacts`

## Step 3: Extract Artifacts

```bash
# Create output directory
mkdir -p release_artifacts

# Extract from Docker image
docker run --rm -v $(pwd)/release_artifacts:/output \
  whisper-xeon-builder sh -c "cp -r /release_artifacts/* /output/"
```

## Step 4: Verify Artifacts

```bash
# Check structure
ls -lh release_artifacts/

# Should show:
# README.md
# push_to_minio.sh
# whisper_small_xeon/
# whisper_medium_xeon/

# Verify library and models
ls -lh release_artifacts/whisper_small_xeon/
# libwhisper.so (~2-5MB)
# ggml-small-q5_1.bin (~140MB)
```

## Step 5: Test with Python (Optional)

```python
import ctypes

lib_path = "release_artifacts/whisper_small_xeon/libwhisper.so"
model_path = "release_artifacts/whisper_small_xeon/ggml-small-q5_1.bin"

whisper = ctypes.CDLL(lib_path)
whisper.whisper_init_from_file.argtypes = [ctypes.c_char_p]
whisper.whisper_init_from_file.restype = ctypes.c_void_p

ctx = whisper.whisper_init_from_file(model_path.encode('utf-8'))
print(f"✓ Context initialized: {ctx is not None}")
```

## Step 6: Upload to MinIO (Optional)

```bash
cd release_artifacts

# Configure MinIO
export MINIO_ENDPOINT="https://minio.example.com"
export MINIO_BUCKET="whisper-artifacts"
export MINIO_ACCESS_KEY="your-key"
export MINIO_SECRET_KEY="your-secret"

# Upload
bash push_to_minio.sh
```

## Step 7: Commit Changes

```bash
# Stage all changes
git add -A

# Commit
git commit -m "chore: implement xeon builder with repository pruning

- Add maintenance_prune.py for repository cleanup
- Update Dockerfile to work with pruned structure
- Add BUILD_ARTIFACTS_USAGE.md and DEPLOYMENT_GUIDE.md
- Update README.md to focus on Xeon builder purpose
- Preserve only essential files for build pipeline
"

# Push (if using remote)
git push
```

## Common Issues & Solutions

### Issue: Docker build fails with missing package-tmpl.json

**Cause:** File wasn't tracked by git or pruning script removed it
**Solution:**
```bash
# Verify file exists and is tracked
ls -la bindings/javascript/package-tmpl.json
git add bindings/javascript/package-tmpl.json
```

### Issue: Pruning script removes too much

**Solution:** Check the whitelist in `maintenance_prune.py`:
- `keep_dirs`: Root-level directories to keep
- `keep_files`: Root-level files to keep
- `keep_example_items`: Specific example paths
- `keep_binding_items`: Required bindings files
- `keep_model_items`: Required model files

### Issue: quantize tool not found

**Cause:** Manual compilation failed
**Solution:** Check Docker build logs for g++ errors

### Issue: Models fail to download

**Cause:** Network issues or Hugging Face timeout
**Solution:** Retry the build - Docker caching will skip completed steps

## File Structure After Pruning

```
whisper-xeon-builder/
├── Dockerfile              # Multi-stage build
├── README.md               # Project documentation
├── BUILD_ARTIFACTS_USAGE.md
├── DEPLOYMENT_GUIDE.md
├── maintenance_prune.py    # Pruning script
├── src/                    # Core library
├── ggml/                   # ML backend
├── include/                # Headers
├── cmake/                  # Build config
├── examples/
│   ├── quantize/          # Quantization tool
│   ├── common.h
│   ├── common.cpp
│   ├── common-ggml.h
│   └── common-ggml.cpp
├── models/
│   ├── download-ggml-model.sh
│   └── download-ggml-model.cmd
├── scripts/               # Build utilities
├── bindings/
│   └── javascript/
│       └── package-tmpl.json  # Required by CMake
└── openspec/              # Change management
```

## Key Points

1. **Pruning First:** Always run pruning before building if you want a clean repository
2. **Git Tracking:** Ensure `bindings/javascript/package-tmpl.json` is tracked by git
3. **Docker Caching:** Subsequent builds are much faster due to layer caching
4. **Self-Contained:** Each model directory (small/medium) is fully independent
5. **Production Ready:** Artifacts can be deployed directly to servers

## Performance Expectations

| Operation | Time (First Run) | Time (Cached) |
|-----------|------------------|---------------|
| Pruning | 1-2 minutes | N/A |
| Docker Build | 20-30 minutes | 5-10 minutes |
| Model Download | 5-10 minutes | Cached |
| Quantization | 2-5 minutes | Cached |
| Total | ~30-45 minutes | ~5-10 minutes |

## Next Steps

See:
- `BUILD_ARTIFACTS_USAGE.md` - Detailed usage guide
- `DEPLOYMENT_GUIDE.md` - Production deployment strategies
- `release_artifacts/README.md` - Generated during build with examples

---

**Ready to build!** Start with Step 1 (pruning) or skip to Step 2 (Docker build).
