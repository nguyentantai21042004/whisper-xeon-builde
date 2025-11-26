# Whisper Xeon Artifacts - Integration Guide

Hướng dẫn tích hợp Whisper artifacts từ MinIO vào các dự án khác.

## 📦 Artifacts Có Gì?

Sau khi build, artifacts được lưu trên MinIO với cấu trúc:

```
whisper-artifacts/
├── whisper_small_xeon/
│   ├── libwhisper.so          # Thư viện Whisper C++ (540 KB)
│   ├── libggml.so.0           # GGML core (47 KB)
│   ├── libggml-base.so.0      # GGML base (625 KB)
│   ├── libggml-cpu.so.0       # GGML CPU backend (649 KB)
│   ├── ggml-small-q5_1.bin    # Model Small quantized (181 MB)
│   └── README.md
│
└── whisper_medium_xeon/
    ├── libwhisper.so          # Thư viện Whisper C++ (540 KB)
    ├── libggml.so.0           # GGML core (47 KB)
    ├── libggml-base.so.0      # GGML base (625 KB)
    ├── libggml-cpu.so.0       # GGML CPU backend (649 KB)
    ├── ggml-medium-q5_1.bin   # Model Medium quantized (1.5 GB)
    └── README.md
```

### Model Specifications

| Model | Parameters | Quantized Size | Speed | Accuracy | Use Case |
|-------|-----------|----------------|-------|----------|----------|
| **Small** | ~244M | 181 MB | Fast | Good | Real-time transcription, quick processing |
| **Medium** | ~769M | 1.5 GB | Moderate | Better | Higher accuracy requirements |

### Library Dependencies

Các file `.so` có dependencies:
- `libwhisper.so` → cần `libggml.so.0`
- `libggml.so.0` → cần `libggml-base.so.0` và `libggml-cpu.so.0`

## 🔧 System Requirements

**Runtime Dependencies:**
- Linux x86_64 (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- CPU với AVX2 và FMA support (Intel Xeon, Core i5/i7/i9 4th gen+)
- `libgomp1` (OpenMP runtime)
- Python 3.8+ (cho Python integration)

**Kiểm tra CPU support:**
```bash
grep -E "avx2|fma" /proc/cpuinfo
```

**Cài đặt dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libgomp1

# CentOS/RHEL
sudo yum install -y libgomp
```

## 📥 Download Artifacts từ MinIO

### Option 1: Sử dụng Python Script (Recommended)

Tạo file `download_whisper_artifacts.py`:

```python
#!/usr/bin/env python3
"""
Download Whisper artifacts from MinIO
"""
import os
import sys
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import ClientError
    from botocore.client import Config
except ImportError:
    print("Error: boto3 not installed. Install with: pip install boto3")
    sys.exit(1)

# MinIO Configuration
MINIO_ENDPOINT = "http://172.16.19.115:9000"  # Thay đổi cho phù hợp
MINIO_ACCESS_KEY = "smap"
MINIO_SECRET_KEY = "hcmut2025"
BUCKET_NAME = "whisper-artifacts"

# Chọn model (small hoặc medium)
MODEL_SIZE = "small"  # hoặc "medium"


def download_artifacts(model_size="small"):
    """Download Whisper artifacts cho một model size"""
    
    # Create output directory
    output_dir = Path(f"whisper_{model_size}_xeon")
    output_dir.mkdir(exist_ok=True)
    
    print(f"📦 Downloading Whisper {model_size.upper()} artifacts...")
    print(f"   Target: {output_dir}/")
    print()
    
    # Create S3 client
    s3_client = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )
    
    # List of files to download
    prefix = f"whisper_{model_size}_xeon/"
    
    try:
        # List objects in bucket
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        
        if 'Contents' not in response:
            print(f"❌ No artifacts found for {model_size} model")
            return False
        
        # Download each file
        for obj in response['Contents']:
            key = obj['Key']
            filename = key.split('/')[-1]
            
            if not filename:  # Skip directory entries
                continue
            
            local_path = output_dir / filename
            file_size_mb = obj['Size'] / (1024 * 1024)
            
            print(f"⬇️  {filename} ({file_size_mb:.1f} MB)...", end=" ", flush=True)
            
            try:
                s3_client.download_file(BUCKET_NAME, key, str(local_path))
                print("✓")
            except ClientError as e:
                print(f"✗ Error: {e}")
                return False
        
        print()
        print(f"✅ Downloaded to: {output_dir}/")
        return True
        
    except ClientError as e:
        print(f"❌ Error accessing MinIO: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        MODEL_SIZE = sys.argv[1].lower()
    
    if MODEL_SIZE not in ["small", "medium"]:
        print("Usage: python download_whisper_artifacts.py [small|medium]")
        sys.exit(1)
    
    success = download_artifacts(MODEL_SIZE)
    sys.exit(0 if success else 1)
```

**Sử dụng:**

```bash
# Cài boto3
pip install boto3

# Download Small model
python download_whisper_artifacts.py small

# Download Medium model
python download_whisper_artifacts.py medium
```

### Option 2: Sử dụng mc (MinIO Client)

```bash
# Cài đặt mc
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/

# Configure MinIO
mc alias set myminio http://172.16.19.115:9000 smap hcmut2025

# Download Small model
mc cp --recursive myminio/whisper-artifacts/whisper_small_xeon/ ./whisper_small_xeon/

# Download Medium model
mc cp --recursive myminio/whisper-artifacts/whisper_medium_xeon/ ./whisper_medium_xeon/
```

### Option 3: Sử dụng curl (Manual)

```bash
# Download từng file bằng presigned URL
# (Cần generate presigned URL từ MinIO Console hoặc API)
```

## 🐍 Python Integration

### Setup

```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài các package cần thiết
pip install numpy scipy
```

### Basic Usage với ctypes

```python
import ctypes
import os
from pathlib import Path

# Load libraries với đúng thứ tự dependencies
lib_dir = Path("whisper_small_xeon")

# Set LD_LIBRARY_PATH để tìm dependencies
os.environ['LD_LIBRARY_PATH'] = str(lib_dir) + ':' + os.environ.get('LD_LIBRARY_PATH', '')

# Load dependencies trước
libggml_base = ctypes.CDLL(str(lib_dir / "libggml-base.so.0"), mode=ctypes.RTLD_GLOBAL)
libggml_cpu = ctypes.CDLL(str(lib_dir / "libggml-cpu.so.0"), mode=ctypes.RTLD_GLOBAL)
libggml = ctypes.CDLL(str(lib_dir / "libggml.so.0"), mode=ctypes.RTLD_GLOBAL)

# Load Whisper
libwhisper = ctypes.CDLL(str(lib_dir / "libwhisper.so"))

# Initialize context
model_path = str(lib_dir / "ggml-small-q5_1.bin")
ctx = libwhisper.whisper_init_from_file(model_path.encode('utf-8'))

if ctx:
    print("✓ Whisper initialized successfully!")
    
    # Sử dụng Whisper API
    # (Xem include/whisper.h để biết các functions có sẵn)
    
    # Free context khi xong
    libwhisper.whisper_free(ctx)
else:
    print("✗ Failed to initialize Whisper")
```

### Advanced: Wrapper Class

```python
import ctypes
import numpy as np
from pathlib import Path

class WhisperTranscriber:
    """Python wrapper cho Whisper C++ library"""
    
    def __init__(self, model_dir="whisper_small_xeon"):
        self.lib_dir = Path(model_dir)
        self._load_libraries()
        self._init_context()
    
    def _load_libraries(self):
        """Load all required libraries"""
        # Pre-load dependencies
        ctypes.CDLL(str(self.lib_dir / "libggml-base.so.0"), mode=ctypes.RTLD_GLOBAL)
        ctypes.CDLL(str(self.lib_dir / "libggml-cpu.so.0"), mode=ctypes.RTLD_GLOBAL)
        ctypes.CDLL(str(self.lib_dir / "libggml.so.0"), mode=ctypes.RTLD_GLOBAL)
        
        # Load Whisper
        self.lib = ctypes.CDLL(str(self.lib_dir / "libwhisper.so"))
        
        # Define function signatures
        self.lib.whisper_init_from_file.argtypes = [ctypes.c_char_p]
        self.lib.whisper_init_from_file.restype = ctypes.c_void_p
        
        self.lib.whisper_free.argtypes = [ctypes.c_void_p]
        self.lib.whisper_free.restype = None
    
    def _init_context(self):
        """Initialize Whisper context"""
        model_path = str(self.lib_dir / "ggml-small-q5_1.bin")
        self.ctx = self.lib.whisper_init_from_file(model_path.encode('utf-8'))
        
        if not self.ctx:
            raise RuntimeError("Failed to initialize Whisper context")
    
    def transcribe(self, audio_file):
        """
        Transcribe audio file
        
        Args:
            audio_file: Path to WAV file (16kHz, mono)
        
        Returns:
            str: Transcribed text
        """
        # TODO: Implement transcription logic
        # See whisper.h for full API
        pass
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'ctx') and self.ctx:
            self.lib.whisper_free(self.ctx)

# Usage
transcriber = WhisperTranscriber("whisper_small_xeon")
# result = transcriber.transcribe("audio.wav")
```

## 🔧 C/C++ Integration

### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.10)
project(MyWhisperApp)

set(CMAKE_CXX_STANDARD 17)

# Whisper artifacts location
set(WHISPER_DIR "${CMAKE_SOURCE_DIR}/whisper_small_xeon")

# Include Whisper header (download từ repo)
include_directories(${CMAKE_SOURCE_DIR}/include)

# Link libraries
link_directories(${WHISPER_DIR})

add_executable(my_app main.cpp)

target_link_libraries(my_app
    ${WHISPER_DIR}/libwhisper.so
    ${WHISPER_DIR}/libggml.so.0
    ${WHISPER_DIR}/libggml-base.so.0
    ${WHISPER_DIR}/libggml-cpu.so.0
    pthread
    m
)

# Set RPATH để tìm .so files
set_target_properties(my_app PROPERTIES
    BUILD_RPATH "${WHISPER_DIR}"
    INSTALL_RPATH "${WHISPER_DIR}"
)
```

### main.cpp

```cpp
#include <iostream>
#include "whisper.h"

int main() {
    // Initialize Whisper
    const char* model_path = "whisper_small_xeon/ggml-small-q5_1.bin";
    struct whisper_context* ctx = whisper_init_from_file(model_path);
    
    if (!ctx) {
        std::cerr << "Failed to initialize Whisper" << std::endl;
        return 1;
    }
    
    std::cout << "Whisper initialized successfully!" << std::endl;
    
    // Use Whisper API
    // ...
    
    // Cleanup
    whisper_free(ctx);
    return 0;
}
```

### Build & Run

```bash
# Download whisper.h header
wget https://raw.githubusercontent.com/ggerganov/whisper.cpp/master/include/whisper.h -P include/

# Build
mkdir build && cd build
cmake ..
make

# Run
./my_app
```

## 🐳 Docker Integration

### Dockerfile

```dockerfile
FROM ubuntu:22.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install boto3 for downloading
RUN pip3 install boto3

# Set working directory
WORKDIR /app

# Copy download script
COPY download_whisper_artifacts.py .

# Download artifacts at build time (hoặc runtime)
ARG MODEL_SIZE=small
RUN python3 download_whisper_artifacts.py ${MODEL_SIZE}

# Copy your application
COPY . .

# Set library path
ENV LD_LIBRARY_PATH=/app/whisper_${MODEL_SIZE}_xeon:$LD_LIBRARY_PATH

CMD ["python3", "your_app.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  whisper-app:
    build:
      context: .
      args:
        MODEL_SIZE: small
    environment:
      - LD_LIBRARY_PATH=/app/whisper_small_xeon
    volumes:
      - ./data:/app/data
    ports:
      - "8000:8000"
```

## 📋 Checklist Tích Hợp

- [ ] Kiểm tra CPU support (AVX2, FMA)
- [ ] Cài đặt `libgomp1`
- [ ] Download artifacts từ MinIO (chọn Small hoặc Medium)
- [ ] Verify các file `.so` và `.bin` đã tải về
- [ ] Set `LD_LIBRARY_PATH` hoặc RPATH
- [ ] Test load libraries thành công
- [ ] Test transcribe với sample audio
- [ ] Optimize cho production (caching, threading, etc.)

## ⚡ Performance Tips

### 1. Model Selection
- **Small model**: Dùng cho real-time, latency-sensitive applications
- **Medium model**: Dùng khi cần accuracy cao hơn, có thể chấp nhận latency

### 2. Thread Configuration
```python
# Set số threads cho Whisper
os.environ['OMP_NUM_THREADS'] = '4'  # Adjust based on CPU cores
```

### 3. Batch Processing
- Process nhiều audio files trong một batch
- Reuse Whisper context thay vì init mỗi lần

### 4. Memory Management
- Small model: ~500 MB RAM
- Medium model: ~2 GB RAM
- Cần thêm RAM cho audio buffer

## 🐛 Troubleshooting

### Library Not Found Error

```
Error: libwhisper.so: cannot open shared object file
```

**Fix:**
```bash
export LD_LIBRARY_PATH=/path/to/whisper_small_xeon:$LD_LIBRARY_PATH
```

### CPU Not Supported

```
Illegal instruction (core dumped)
```

**Check:**
```bash
grep -E "avx2|fma" /proc/cpuinfo
```

CPU phải support AVX2 và FMA.

### Memory Issues

```
Failed to allocate memory
```

**Solutions:**
- Dùng Small model thay vì Medium
- Tăng RAM cho container/VM
- Giảm batch size

## 📚 Additional Resources

- **Whisper C API**: [include/whisper.h](https://github.com/ggerganov/whisper.cpp/blob/master/include/whisper.h)
- **Original Whisper.cpp**: https://github.com/ggerganov/whisper.cpp
- **OpenAI Whisper**: https://github.com/openai/whisper
- **MinIO Documentation**: https://min.io/docs/minio/linux/index.html

## 💬 Support

Nếu gặp vấn đề khi tích hợp:
1. Kiểm tra checklist trên
2. Xem logs chi tiết
3. Verify CPU support và dependencies
4. Test với sample audio nhỏ trước

---

**Version**: 1.0  
**Last Updated**: 2025-11-26  
**Maintained by**: Whisper Xeon Builder Team

