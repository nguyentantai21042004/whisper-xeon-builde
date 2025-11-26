# Stage 1: Builder
FROM ubuntu:22.04 AS builder

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Build libwhisper.so with AVX2 and FMA optimizations
# -DGGML_AVX2=ON and -DGGML_FMA=ON are usually default on x86, but we force them for Xeon optimization.
# -DBUILD_SHARED_LIBS=ON to build libwhisper.so
RUN cmake -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_AVX2=ON \
    -DGGML_FMA=ON \
    -DBUILD_SHARED_LIBS=ON \
    && cmake --build build --config Release -j$(nproc)

# Build quantize tool (it might be built by default, but ensuring it exists)
RUN cmake --build build --target quantize --config Release -j$(nproc)

# Download and Quantize Models
# We need 'small' and 'medium' models.
# The download script is in models/download-ggml-model.sh
RUN chmod +x models/download-ggml-model.sh

# Download and quantize Small model
RUN ./models/download-ggml-model.sh small \
    && ./build/bin/quantize models/ggml-small.bin models/ggml-small-q5_1.bin q5_1

# Download and quantize Medium model
RUN ./models/download-ggml-model.sh medium \
    && ./build/bin/quantize models/ggml-medium.bin models/ggml-medium-q5_1.bin q5_1

# Stage 2: Organizer
FROM ubuntu:22.04 AS organizer

WORKDIR /release_artifacts

# Create directory structure
RUN mkdir -p whisper_small_xeon whisper_medium_xeon

# Copy artifacts from builder
# Library is located in build/src/
COPY --from=builder /app/build/src/libwhisper.so /release_artifacts/whisper_small_xeon/
COPY --from=builder /app/build/src/libwhisper.so /release_artifacts/whisper_medium_xeon/

# Copy libggml dependencies
COPY --from=builder /app/build/ggml/src/libggml.so.0 /release_artifacts/whisper_small_xeon/
COPY --from=builder /app/build/ggml/src/libggml-base.so.0 /release_artifacts/whisper_small_xeon/
COPY --from=builder /app/build/ggml/src/libggml-cpu.so.0 /release_artifacts/whisper_small_xeon/

COPY --from=builder /app/build/ggml/src/libggml.so.0 /release_artifacts/whisper_medium_xeon/
COPY --from=builder /app/build/ggml/src/libggml-base.so.0 /release_artifacts/whisper_medium_xeon/
COPY --from=builder /app/build/ggml/src/libggml-cpu.so.0 /release_artifacts/whisper_medium_xeon/

COPY --from=builder /app/models/ggml-small-q5_1.bin /release_artifacts/whisper_small_xeon/
COPY --from=builder /app/models/ggml-medium-q5_1.bin /release_artifacts/whisper_medium_xeon/

# Generate README.md (Task 3)
RUN echo '# Whisper Xeon Artifacts' > README.md && \
    echo '' >> README.md && \
    echo '## Overview' >> README.md && \
    echo 'This package contains Xeon-optimized Whisper artifacts (AVX2/FMA enabled) and quantized models.' >> README.md && \
    echo '' >> README.md && \
    echo '## Structure' >> README.md && \
    echo '- `whisper_small_xeon/`: Contains `libwhisper.so` and `ggml-small-q5_1.bin`' >> README.md && \
    echo '- `whisper_medium_xeon/`: Contains `libwhisper.so` and `ggml-medium-q5_1.bin`' >> README.md && \
    echo '' >> README.md && \
    echo '## Python Integration' >> README.md && \
    echo '```python' >> README.md && \
    echo 'import ctypes' >> README.md && \
    echo 'lib = ctypes.CDLL("./libwhisper.so")' >> README.md && \
    echo '# ... usage ...' >> README.md && \
    echo '```' >> README.md && \
    echo '' >> README.md && \
    echo '## System Requirements' >> README.md && \
    echo '- Linux x86_64' >> README.md && \
    echo '- CPU with AVX2 and FMA support' >> README.md && \
    echo '- libgomp1 (OpenMP runtime)' >> README.md

# Copy README to subdirectories
RUN cp README.md whisper_small_xeon/ && \
    cp README.md whisper_medium_xeon/

# Generate push_to_minio.sh (Task 4)
RUN echo '#!/bin/bash' > push_to_minio.sh && \
    echo 'set -e' >> push_to_minio.sh && \
    echo '' >> push_to_minio.sh && \
    echo '# Configuration' >> push_to_minio.sh && \
    echo 'MINIO_ALIAS=${MINIO_ALIAS:-myminio}' >> push_to_minio.sh && \
    echo 'BUCKET=${BUCKET:-whisper-artifacts}' >> push_to_minio.sh && \
    echo '' >> push_to_minio.sh && \
    echo '# Check for mc' >> push_to_minio.sh && \
    echo 'if ! command -v mc &> /dev/null; then' >> push_to_minio.sh && \
    echo '    echo "Error: mc (MinIO Client) is not installed."' >> push_to_minio.sh && \
    echo '    exit 1' >> push_to_minio.sh && \
    echo 'fi' >> push_to_minio.sh && \
    echo '' >> push_to_minio.sh && \
    echo '# Upload' >> push_to_minio.sh && \
    echo 'echo "Uploading artifacts to $MINIO_ALIAS/$BUCKET..."' >> push_to_minio.sh && \
    echo 'mc cp --recursive whisper_small_xeon/ $MINIO_ALIAS/$BUCKET/whisper_small_xeon/' >> push_to_minio.sh && \
    echo 'mc cp --recursive whisper_medium_xeon/ $MINIO_ALIAS/$BUCKET/whisper_medium_xeon/' >> push_to_minio.sh && \
    echo 'echo "Upload complete."' >> push_to_minio.sh && \
    chmod +x push_to_minio.sh

# Stage 3: Output
# Minimal image to hold the artifacts
FROM alpine:latest AS output

WORKDIR /
COPY --from=organizer /release_artifacts /release_artifacts

# Default command to list artifacts
CMD ["ls", "-R", "/release_artifacts"]
