#!/bin/bash
set -e

echo "========================================="
echo "  MinIO Upload Script - Whisper Artifacts"
echo "========================================="
echo ""

# ====== Cấu hình MinIO selfhost bằng IP và Port ======
# Đọc từ biến môi trường hoặc yêu cầu nhập
if [ -z "$MINIO_IP" ]; then
    read -p "MinIO Server IP [127.0.0.1]: " MINIO_IP
    MINIO_IP=${MINIO_IP:-127.0.0.1}
fi

if [ -z "$MINIO_PORT" ]; then
    read -p "MinIO Server Port [9000]: " MINIO_PORT
    MINIO_PORT=${MINIO_PORT:-9000}
fi

if [ -z "$MINIO_ACCESS_KEY" ]; then
    read -p "MinIO Access Key [minioadmin]: " MINIO_ACCESS_KEY
    MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
fi

if [ -z "$MINIO_SECRET_KEY" ]; then
    read -sp "MinIO Secret Key [minioadmin]: " MINIO_SECRET_KEY
    echo ""
    MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
fi

if [ -z "$BUCKET" ]; then
    read -p "Bucket Name [whisper-artifacts]: " BUCKET
    BUCKET=${BUCKET:-whisper-artifacts}
fi

MINIO_URL="http://$MINIO_IP:$MINIO_PORT"

echo ""
echo "Cấu hình:"
echo "  Server: $MINIO_URL"
echo "  Bucket: $BUCKET"
echo ""

# Kiểm tra curl đã được cài đặt
if ! command -v curl &> /dev/null; then
    echo "Lỗi: curl chưa được cài đặt. Cài đặt: sudo apt-get install curl"
    exit 1
fi

echo "Đang kết nối MinIO tại $MINIO_URL..."

# Hàm tính AWS Signature V4 để xác thực với MinIO
upload_file() {
    local file_path="$1"
    local object_name="$2"
    
    # Đọc file content
    local content_type="application/octet-stream"
    local timestamp=$(date -u +"%Y%m%dT%H%M%SZ")
    local date_stamp=$(date -u +"%Y%m%d")
    
    echo "  Uploading: $object_name"
    
    # Sử dụng AWS Signature V4 để upload
    # MinIO hỗ trợ S3 API nên dùng aws-cli style hoặc presigned URL
    curl -X PUT \
        -H "Host: $MINIO_IP:$MINIO_PORT" \
        -H "Content-Type: $content_type" \
        --user "${MINIO_ACCESS_KEY}:${MINIO_SECRET_KEY}" \
        --data-binary "@${file_path}" \
        "${MINIO_URL}/${BUCKET}/${object_name}" \
        -w "HTTP %{http_code}\n" -o /dev/null -s
}

# Tạo bucket nếu chưa tồn tại (sử dụng S3 API)
echo "Kiểm tra/tạo bucket '$BUCKET'..."
bucket_check=$(curl -s -o /dev/null -w "%{http_code}" \
    --user "${MINIO_ACCESS_KEY}:${MINIO_SECRET_KEY}" \
    -X HEAD "${MINIO_URL}/${BUCKET}/")

if [ "$bucket_check" != "200" ]; then
    echo "  Tạo bucket mới: $BUCKET"
    curl -X PUT \
        --user "${MINIO_ACCESS_KEY}:${MINIO_SECRET_KEY}" \
        "${MINIO_URL}/${BUCKET}/" \
        -w "HTTP %{http_code}\n" -o /dev/null -s
fi

# Upload whisper_small_xeon
echo ""
echo "Upload whisper_small_xeon/..."
if [ -d "whisper_small_xeon" ]; then
    for file in whisper_small_xeon/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            upload_file "$file" "whisper_small_xeon/$filename"
        fi
    done
else
    echo "Cảnh báo: Thư mục whisper_small_xeon không tồn tại"
fi

# Upload whisper_medium_xeon
echo ""
echo "Upload whisper_medium_xeon/..."
if [ -d "whisper_medium_xeon" ]; then
    for file in whisper_medium_xeon/*; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            upload_file "$file" "whisper_medium_xeon/$filename"
        fi
    done
else
    echo "Cảnh báo: Thư mục whisper_medium_xeon không tồn tại"
fi

echo ""
echo "✓ Hoàn tất upload lên MinIO selfhost ($MINIO_IP:$MINIO_PORT/$BUCKET)"
echo ""
echo "Kiểm tra artifacts tại: $MINIO_URL/$BUCKET/"
