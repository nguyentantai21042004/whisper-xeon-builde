# Whisper Xeon Artifacts

## Overview
This package contains Xeon-optimized Whisper artifacts (AVX2/FMA enabled) and quantized models.

## Structure
- `whisper_small_xeon/`: Contains `libwhisper.so` and `ggml-small-q5_1.bin`
- `whisper_medium_xeon/`: Contains `libwhisper.so` and `ggml-medium-q5_1.bin`

## Python Integration
```python
import ctypes
lib = ctypes.CDLL("./libwhisper.so")
# ... usage ...
```

## System Requirements
- Linux x86_64
- CPU with AVX2 and FMA support
- libgomp1 (OpenMP runtime)

## Uploading Artifacts to MinIO (Self-Hosted)

To use the `push_to_minio.sh` script for uploading artifacts, you may need to provide your MinIO server connection info via environment variables.  
**Example usage:**

```bash
export MINIO_IP=<your-minio-ip>
export MINIO_PORT=<your-minio-port>
export MINIO_ACCESS_KEY=<your-access-key>
export MINIO_SECRET_KEY=<your-secret-key>
export BUCKET=<your-bucket-name>
# Run upload script from inside artifacts/ directory:
bash push_to_minio.sh
```

If you omit these, the script will default to:
- MINIO_IP=127.0.0.1
- MINIO_PORT=9000
- MINIO_ACCESS_KEY=minioadmin
- MINIO_SECRET_KEY=minioadmin
- BUCKET=whisper-artifacts

**New:** The script now uses `curl` (no need for `mc` MinIO Client).  
The script will automatically create the bucket if it does not exist, and upload both `whisper_small_xeon/` and `whisper_medium_xeon/` directories using MinIO's S3-compatible API.
