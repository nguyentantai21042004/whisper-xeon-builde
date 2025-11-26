# Project Context

## Purpose
High-performance inference of OpenAI's Whisper automatic speech recognition (ASR) model. The project aims to provide a lightweight, plain C/C++ implementation with zero runtime memory allocations and support for a wide range of platforms and hardware accelerators (Apple Silicon, AVX, CUDA, OpenVINO, etc.).

## Tech Stack
- **Languages**: C, C++ (Core), Python (Scripts/Tests), JavaScript/TypeScript (Web/Bindings)
- **Build Systems**: CMake, Makefile
- **Core Libraries**: ggml (Tensor library)
- **CI/CD**: GitHub Actions

## Project Conventions

### Code Style
- **Core**: Plain C/C++ without third-party dependencies.
- **API**: C-style API defined in `include/whisper.h`.
- **Memory**: Manual memory management, zero runtime allocations preferred.
- **Compatibility**: Broad platform support (Mac, iOS, Android, Linux, WebAssembly, Windows).

### Architecture Patterns
- **Monorepo-like**: Core library (`src`, `include`), bindings (`bindings`), examples (`examples`), and tests (`tests`) in one repo.
- **ggml Integration**: Heavily relies on `ggml` for tensor operations and hardware acceleration.
- **Model Format**: Uses custom `ggml` binary format for models (converted from PyTorch).

### Testing Strategy
- **Unit Tests**: Located in `tests/` directory (C/C++).
- **Integration Tests**: `run-tests.sh` script for running various test scenarios.
- **CI**: Automated testing via GitHub Actions workflows.

### Git Workflow
- **Branching**: PR-based workflow targeting `master`.
- **Versioning**: Semantic versioning (e.g., v1.8.2).

## Domain Context
- **ASR**: Automatic Speech Recognition.
- **Inference**: Running pre-trained models to generate text from audio.
- **Quantization**: Reducing model precision (e.g., 4-bit, 5-bit, 8-bit integers) to save memory and improve performance.
- **Hardware Acceleration**: Utilizing specific hardware instructions (AVX, NEON) and APIs (Metal, CUDA, OpenVINO, Core ML) for speed.

## Important Constraints
- **No Dependencies**: Core implementation must remain dependency-free.
- **Portability**: Must compile and run on a wide variety of architectures and OSes.
- **Performance**: Critical focus on inference speed and memory efficiency.

## External Dependencies
- **ggml**: Machine learning library (bundled/submodule).
- **Optional**:
    - **SDL2**: For audio capture in stream examples.
    - **FFmpeg**: For audio format conversion (optional build flag).
    - **Accelerators**: CUDA, OpenVINO, Core ML, CANN, etc. (depending on build configuration).
