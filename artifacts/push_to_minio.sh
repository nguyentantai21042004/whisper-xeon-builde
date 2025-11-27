#!/bin/bash
set -e

# Configuration
MINIO_ALIAS=${MINIO_ALIAS:-myminio}
BUCKET=${BUCKET:-whisper-artifacts}

# Check for mc
if ! command -v mc &> /dev/null; then
    echo "Error: mc (MinIO Client) is not installed."
    exit 1
fi

# Upload
echo "Uploading artifacts to $MINIO_ALIAS/$BUCKET..."
mc cp --recursive whisper_base_xeon/ $MINIO_ALIAS/$BUCKET/whisper_base_xeon/
mc cp --recursive whisper_small_xeon/ $MINIO_ALIAS/$BUCKET/whisper_small_xeon/
mc cp --recursive whisper_medium_xeon/ $MINIO_ALIAS/$BUCKET/whisper_medium_xeon/
echo "Upload complete."
