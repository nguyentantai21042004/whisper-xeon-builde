# Whisper Xeon Artifacts Build System

## 1. Building the Docker Image (Task 6.1)

To build the Xeon-optimized artifacts, run the following command from the root of the repository:

```bash
docker build -t whisper-xeon-builder .
```

This process will:
1.  Compile `libwhisper.so` with AVX2 and FMA optimizations.
2.  Download and quantize Small and Medium models.
3.  Package everything into the `/release_artifacts` directory inside the image.

## 2. Extracting Artifacts (Task 6.2)

Once the image is built, you can extract the artifacts to your host machine:

```bash
# Create a local directory for output
mkdir -p artifacts

# Run a temporary container to copy files
docker run --rm -v $(pwd)/artifacts:/output whisper-xeon-builder sh -c "cp -r /release_artifacts/* /output/"
```

You will now have `whisper_small_xeon` and `whisper_medium_xeon` directories in your local `artifacts` folder.

## 3. Deployment Examples (Task 6.3)

### Python Integration

Ensure `libwhisper.so` is in your library path or referenced directly.

```python
import ctypes
import os

# Load the library
lib_path = os.path.abspath("./whisper_small_xeon/libwhisper.so")
lib = ctypes.CDLL(lib_path)

# Example: Initialize context (simplified)
# ctx = lib.whisper_init_from_file("whisper_small_xeon/ggml-small-q5_1.bin".encode('utf-8'))
```

### Environment Variables

Set `LD_LIBRARY_PATH` if you want to link dynamically without absolute paths:

```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/whisper_small_xeon
```

## 4. MinIO Upload (Task 6.4)

The build includes a `push_to_minio.sh` script in the artifacts.

**Requirements:**
- `mc` (MinIO Client) installed and configured.
- Alias set for your MinIO server (default: `myminio`).
- Target bucket exists (default: `whisper-artifacts`).

**Usage:**

```bash
# Configure environment
export MINIO_ALIAS=myminio
export BUCKET=my-whisper-bucket

# Run the script (from within the extracted artifacts or container)
./whisper_small_xeon/push_to_minio.sh
```

## 5. Troubleshooting (Task 6.5)

-   **Build fails on AVX2**: Ensure your build host supports AVX2 if you are running tests during build (though cross-compilation usually works, running binaries might fail).
-   **Download fails**: Check internet connectivity for downloading models from Hugging Face.
-   **Docker memory**: Quantization might require significant RAM. Increase Docker memory limit if it crashes (4GB+ recommended).

## 6. Performance Benchmarking (Task 6.6)

To verify performance gains:
1.  Run `whisper-bench` (if built) or a sample inference script using the new `libwhisper.so`.
2.  Compare inference time against the generic build.
3.  Verify `AVX2 = 1` and `FMA = 1` in the system info output of whisper.cpp.
