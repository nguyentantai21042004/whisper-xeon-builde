# Whisper Xeon Artifacts

## Overview
This package contains Xeon-optimized Whisper artifacts (AVX2/FMA enabled) and quantized models.

## Structure
- `whisper_base_xeon/`: Contains `libwhisper.so` and `ggml-base-q5_1.bin`
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
