#!/bin/bash
set -e

# Cấu hình kết nối tới MinIO self-host (tùy chỉnh theo hệ thống của bạn)
# Ví dụ:
# MINIO_ALIAS tên đã cấu hình bằng `mc alias set`
MINIO_ALIAS=${MINIO_ALIAS:-seflhost-minio}
BUCKET=${BUCKET:-whisper-artifacts}

# Kiểm tra lệnh mc (MinIO Client)
if ! command -v mc &> /dev/null; then
    echo "Lỗi: mc (MinIO Client) chưa được cài đặt."
    exit 1
fi

# Kiểm tra alias đã tồn tại chưa (tùy chọn, có thể bỏ qua nếu chắc chắn alias đã cấu hình)
/usr/bin/mc alias list | grep -q "$MINIO_ALIAS" || {
    echo "Lỗi: Alias MinIO '$MINIO_ALIAS' chưa được cấu hình. Vui lòng cấu hình bằng:"
    echo "mc alias set $MINIO_ALIAS http://<url>:9000 <ACCESS_KEY> <SECRET_KEY>"
    exit 1
}

# Upload artifacts lên bucket MinIO selfhost
echo "Đang upload artifacts lên $MINIO_ALIAS/$BUCKET..."
mc cp --recursive whisper_small_xeon/ "$MINIO_ALIAS/$BUCKET/whisper_small_xeon/"
mc cp --recursive whisper_medium_xeon/ "$MINIO_ALIAS/$BUCKET/whisper_medium_xeon/"
echo "Upload hoàn tất lên MinIO selfhost."
