# Repository Pruning - Fixes Applied

## Problem
After running `maintenance_prune.py`, the Docker build failed with CMake errors:
1. Missing `bindings/javascript/package-tmpl.json` (required by root CMakeLists.txt)
2. Missing `tests/` directory (referenced in CMakeLists.txt)
3. Missing example directories (referenced in examples/CMakeLists.txt)

## Solution

### 1. Updated `maintenance_prune.py`
Added whitelist for essential build files:

```python
# Keep minimal bindings files (needed by CMakeLists.txt)
self.keep_binding_items = {
    'bindings/javascript/package-tmpl.json',  # Required by root CMakeLists.txt
}
```

Updated pruning logic to handle `bindings/` directory selectively.

### 2. Created Required Files
Manually created the minimal bindings structure:
```bash
mkdir -p bindings/javascript
# Created bindings/javascript/package-tmpl.json with minimal template
```

### 3. Updated Dockerfile
Added CMake flag to disable building tests:
```dockerfile
RUN cmake -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_AVX2=ON \
    -DGGML_FMA=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DWHISPER_BUILD_TESTS=OFF \    # <-- Added this
    && cmake --build build --config Release -j$(nproc)
```

## Verification

The Docker build now completes successfully:
```bash
docker build -t whisper-xeon-builder .
```

## Running the Pruning Script

To prune the repository while keeping all required build files:

```bash
# Preview what will be removed
python3 maintenance_prune.py --dry-run

# Execute pruning
python3 maintenance_prune.py
```

The updated script now properly handles:
- ✅ Keeps `bindings/javascript/package-tmpl.json`
- ✅ Keeps `examples/quantize/` and essential common files
- ✅ Keeps `scripts/` directory
- ✅ Keeps `models/download-ggml-model.sh`
- ✅ Removes non-essential bindings, examples, tests, samples

## What Gets Removed

The script removes approximately 78 items:
- Most of `bindings/` (except package-tmpl.json)
- Most of `examples/` (except quantize and common files)
- All of `tests/` directory contents
- `samples/` directory
- Various platform-specific files (build-xcframework.sh, etc.)
- Temporary files (AGENTS.md, term.md, etc.)

## What Gets Kept

~1115 essential items including:
- All core source (`src/`, `ggml/`, `include/`)
- Build configuration (`cmake/`, `CMakeLists.txt`, `Makefile`)
- Essential tools (`examples/quantize/`)
- Build scripts (`scripts/`, `models/download-ggml-model.sh`)
- Documentation (`BUILD_ARTIFACTS_USAGE.md`, `DEPLOYMENT_GUIDE.md`, `README.md`)
- Project management (`openspec/`, `.github/`, `.claude/`, `.cursor/`)
- Main Dockerfile and build configuration

## Notes

- The repository can now be pruned and still build successfully
- All required files for the Xeon builder pipeline are preserved
- The pruned repository focuses solely on the build and packaging workflow
