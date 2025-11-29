#!/bin/bash
set -e

# Image name
IMAGE_NAME="whisper-xeon-builder"
CONTAINER_NAME="whisper-xeon-extractor"
OUTPUT_DIR="artifacts"

echo "========================================================"
echo "Building Whisper for Linux x86_64 (Xeon Optimized)"
echo "========================================================"
echo "Note: This may take a while on Apple Silicon due to emulation."
echo ""

# 1. Build the Docker image for linux/amd64
echo "[1/4] Building Docker image..."
docker build --platform linux/amd64 -t $IMAGE_NAME .

# 2. Create a temporary container
echo "[2/4] Creating temporary container..."
# Remove existing container if it exists
docker rm -f $CONTAINER_NAME 2>/dev/null || true
docker create --platform linux/amd64 --name $CONTAINER_NAME $IMAGE_NAME

# 3. Copy artifacts
echo "[3/4] Extracting artifacts to ./$OUTPUT_DIR..."
rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR
docker cp $CONTAINER_NAME:/release_artifacts/. $OUTPUT_DIR/

# 4. Clean up
echo "[4/4] Cleaning up..."
docker rm -f $CONTAINER_NAME

echo ""
echo "========================================================"
echo "Build Complete!"
echo "========================================================"
echo "Artifacts are in: ./$OUTPUT_DIR"
echo ""
echo "Verifying architecture of libwhisper.so:"
file $OUTPUT_DIR/whisper_base_xeon/libwhisper.so
echo ""
echo "If it says 'x86-64', you are good to go!"
