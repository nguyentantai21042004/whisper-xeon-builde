# Capability: Build Automation

## ADDED Requirements

### Requirement: Multi-Stage Docker Build Pipeline

The system SHALL provide a multi-stage Dockerfile that automates compilation of libwhisper.so optimized for Intel Xeon processors (AVX2/FMA) and quantization of Whisper models.

#### Scenario: Successful Docker build execution

- **WHEN** user runs `docker build -t whisper-builder .`
- **THEN** the build completes successfully through all stages
- **AND** the final image contains `/release_artifacts` directory
- **AND** no build errors or warnings are reported for critical components

#### Scenario: AVX2 and FMA optimizations enabled

- **WHEN** CMake configuration is executed in builder stage
- **THEN** `-DGGML_AVX2=ON` flag is set
- **AND** `-DGGML_FMA=ON` flag is set
- **AND** `-DBUILD_SHARED_LIBS=ON` flag is set
- **AND** the compiled library includes AVX2/FMA CPU optimizations

#### Scenario: Shared library compilation

- **WHEN** the builder stage compiles whisper.cpp
- **THEN** `libwhisper.so` shared library is generated
- **AND** the library is compatible with Linux x86_64 architecture
- **AND** the library can be loaded via ctypes in Python

### Requirement: Automated Model Download and Quantization

The system SHALL automatically download Whisper Small and Medium base models and quantize them to q5_1 format using the built quantize tool.

#### Scenario: Model download from Hugging Face

- **WHEN** the builder stage executes model download
- **THEN** `ggml-small.bin` base model is downloaded successfully
- **AND** `ggml-medium.bin` base model is downloaded successfully
- **AND** downloads use existing `models/download-ggml-model.sh` script

#### Scenario: Model quantization to q5_1

- **WHEN** quantization is performed on downloaded models
- **THEN** `ggml-small-q5_1.bin` is generated from small base model
- **AND** `ggml-medium-q5_1.bin` is generated from medium base model
- **AND** quantized models maintain compatibility with whisper.cpp inference
- **AND** quantization uses the `examples/quantize/quantize` tool

#### Scenario: Quantization error handling

- **WHEN** quantization fails for any model
- **THEN** the build process stops with clear error message
- **AND** the error indicates which model failed to quantize

### Requirement: Standardized Artifact Packaging Structure

The system SHALL organize build outputs into a standardized directory structure where each model variant has a self-contained folder with both library and model files.

#### Scenario: Release artifacts directory structure

- **WHEN** packaging stage completes
- **THEN** `/release_artifacts` directory exists
- **AND** it contains `whisper_small_xeon/` subdirectory
- **AND** it contains `whisper_medium_xeon/` subdirectory
- **AND** it contains `README.md` file
- **AND** it contains `push_to_minio.sh` script

#### Scenario: Self-contained model directories

- **WHEN** examining `whisper_small_xeon/` directory
- **THEN** it contains `libwhisper.so` file
- **AND** it contains `ggml-small-q5_1.bin` file
- **AND** no other dependencies are required for operation
- **AND** the same structure applies to `whisper_medium_xeon/` with its respective model file

#### Scenario: Directory independence

- **WHEN** copying a single model directory to another system
- **THEN** the directory operates independently without external dependencies
- **AND** both library and model are present in the copied directory
- **AND** no path resolution or symlink configuration is needed

### Requirement: Deployment Documentation Generation

The system SHALL automatically generate README.md with complete usage instructions including Python ctypes integration examples and MinIO upload guidance.

#### Scenario: README content completeness

- **WHEN** README.md is generated
- **THEN** it contains overview of artifact structure
- **AND** it contains Python ctypes code example for loading libwhisper.so
- **AND** it contains model path configuration examples
- **AND** it contains MinIO upload script usage instructions
- **AND** it documents system requirements (Linux, x86_64, glibc version)

#### Scenario: Python integration example validity

- **WHEN** Python code example is extracted from README
- **THEN** the example demonstrates ctypes.CDLL loading
- **AND** the example shows proper library and model path configuration
- **AND** the example includes basic whisper context initialization
- **AND** the code is syntactically correct and runnable

### Requirement: MinIO Storage Upload Automation

The system SHALL provide a shell script that automates uploading the release artifacts directory to MinIO storage using standard CLI tools.

#### Scenario: MinIO upload script generation

- **WHEN** packaging completes
- **THEN** `push_to_minio.sh` script is created in `/release_artifacts`
- **AND** the script is executable (chmod +x)
- **AND** the script supports both `mc` and `aws s3` CLI tools
- **AND** the script includes configuration placeholders for endpoint and bucket

#### Scenario: Script execution with mc client

- **WHEN** user runs `bash push_to_minio.sh` with mc installed
- **THEN** the script detects mc availability
- **AND** it uploads all files in `whisper_small_xeon/` directory
- **AND** it uploads all files in `whisper_medium_xeon/` directory
- **AND** it preserves directory structure in MinIO bucket
- **AND** it reports upload success or failure for each file

#### Scenario: Script configuration validation

- **WHEN** push_to_minio.sh is executed without configuration
- **THEN** the script provides helpful error message
- **AND** it indicates which environment variables need to be set
- **AND** it provides example values for MinIO endpoint and bucket configuration

### Requirement: Build Reproducibility and Artifact Extraction

The system SHALL enable reproducible builds and provide mechanisms to extract artifacts from Docker containers to the host filesystem.

#### Scenario: Docker image build reproducibility

- **WHEN** the same Dockerfile is built multiple times
- **THEN** each build produces functionally identical artifacts
- **AND** library files have consistent behavior across builds
- **AND** quantized models are bit-identical for same input models

#### Scenario: Artifact extraction to host

- **WHEN** user runs Docker container with volume mount
- **THEN** `/release_artifacts` can be copied to host filesystem
- **AND** the extracted artifacts function identically to in-container versions
- **AND** file permissions are preserved during extraction

#### Scenario: Build from clean state

- **WHEN** Docker build is executed with `--no-cache` flag
- **THEN** all stages execute from scratch
- **AND** build completes successfully without cached layers
- **AND** final artifacts match cached build outputs functionally
