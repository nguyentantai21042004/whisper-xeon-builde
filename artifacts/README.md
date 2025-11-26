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

Simply run the upload script:

```bash
./push_to_minio.sh
```

The script will **interactively ask** for your MinIO connection details with sensible defaults:
- MinIO Server IP (default: 127.0.0.1)
- MinIO Server Port (default: 9000)
- Access Key (default: minioadmin)
- Secret Key (default: minioadmin, hidden input)
- Bucket Name (default: whisper-artifacts)

**For automated environments** (CI/CD), pre-set environment variables:

```bash
export MINIO_IP=192.168.1.100
export MINIO_PORT=9000
export MINIO_ACCESS_KEY=your-access-key
export MINIO_SECRET_KEY=your-secret-key
export BUCKET=whisper-artifacts
./push_to_minio.sh  # Skips all prompts
```

**Features:**
- Uses `curl` (no need for `mc` MinIO Client)
- Auto-creates bucket if it doesn't exist
- Uploads both `whisper_small_xeon/` and `whisper_medium_xeon/`
- Uses MinIO's S3-compatible API
