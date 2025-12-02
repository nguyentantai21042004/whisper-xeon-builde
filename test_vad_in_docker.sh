#!/bin/bash
# Test VAD disabled in Docker container (Linux x86_64)

set -e

echo "=============================================="
echo "Testing VAD in Docker (Linux x86_64)"
echo "=============================================="

# Check if artifacts exist
if [ ! -d "artifacts/whisper_base_xeon" ]; then
    echo "Error: artifacts/whisper_base_xeon not found"
    echo "Please run ./build_release_x86.sh first"
    exit 1
fi

# Create a temporary Dockerfile for testing
cat > Dockerfile.test << 'EOF'
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /test

# Copy test script and artifacts
COPY test_vad_disabled.py /test/
COPY artifacts/whisper_base_xeon /test/whisper_base_xeon/

# Run test
CMD ["python3", "test_vad_disabled.py", "whisper_base_xeon"]
EOF

echo ""
echo "[1/3] Building test Docker image..."
docker build --platform linux/amd64 -t whisper-vad-test -f Dockerfile.test .

echo ""
echo "[2/3] Running VAD test in container..."
docker run --platform linux/amd64 --rm whisper-vad-test

echo ""
echo "[3/3] Cleaning up..."
rm -f Dockerfile.test

echo ""
echo "=============================================="
echo "Test complete!"
echo "=============================================="
