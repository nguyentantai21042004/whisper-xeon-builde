#!/usr/bin/env python3
"""
MinIO Upload Script - Whisper Artifacts
Uses boto3 (AWS SDK) which is compatible with MinIO
"""

import os
import sys
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import ClientError
    from botocore.client import Config
except ImportError:
    print("Error: boto3 is not installed.")
    print("Install it with: pip install boto3")
    sys.exit(1)


def get_input(prompt, default=""):
    """Get user input with default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def get_config():
    """Get MinIO configuration from env vars or user input."""
    print("=" * 50)
    print("  MinIO Upload Script - Whisper Artifacts")
    print("=" * 50)
    print()
    
    config = {}
    
    # Read from environment or prompt
    config['endpoint'] = os.environ.get('MINIO_IP') or get_input("MinIO Server IP", "127.0.0.1")
    config['port'] = os.environ.get('MINIO_PORT') or get_input("MinIO Server Port", "9000")
    config['access_key'] = os.environ.get('MINIO_ACCESS_KEY') or get_input("MinIO Access Key", "minioadmin")
    
    # Secret key - use getpass if available for hidden input
    secret_key = os.environ.get('MINIO_SECRET_KEY')
    if not secret_key:
        try:
            import getpass
            secret_key = getpass.getpass(f"MinIO Secret Key [minioadmin]: ") or "minioadmin"
        except:
            secret_key = get_input("MinIO Secret Key", "minioadmin")
    config['secret_key'] = secret_key
    
    config['bucket'] = os.environ.get('BUCKET') or get_input("Bucket Name", "whisper-artifacts")
    
    config['endpoint_url'] = f"http://{config['endpoint']}:{config['port']}"
    
    print()
    print("Cấu hình:")
    print(f"  Server: {config['endpoint_url']}")
    print(f"  Bucket: {config['bucket']}")
    print()
    
    return config


def upload_directory(s3_client, bucket_name, local_dir, s3_prefix):
    """Upload all files from a directory to S3/MinIO."""
    local_path = Path(local_dir)
    
    if not local_path.exists():
        print(f"⚠️  Thư mục không tồn tại: {local_dir}")
        return
    
    files = list(local_path.glob("*"))
    if not files:
        print(f"⚠️  Không có file nào trong: {local_dir}")
        return
    
    print(f"📁 Upload {local_dir}/ ({len(files)} files)...")
    
    for file_path in files:
        if file_path.is_file():
            object_name = f"{s3_prefix}/{file_path.name}"
            try:
                file_size = file_path.stat().st_size
                size_mb = file_size / (1024 * 1024)
                
                print(f"  ⬆️  {file_path.name} ({size_mb:.1f} MB)...", end=" ", flush=True)
                
                s3_client.upload_file(
                    str(file_path),
                    bucket_name,
                    object_name
                )
                
                print("✓")
            except ClientError as e:
                print(f"✗ Lỗi: {e}")


def main():
    # Get configuration
    config = get_config()
    
    # Create S3 client configured for MinIO
    print(f"🔌 Đang kết nối MinIO tại {config['endpoint_url']}...")
    
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=config['endpoint_url'],
            aws_access_key_id=config['access_key'],
            aws_secret_access_key=config['secret_key'],
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'  # MinIO doesn't care about region but boto3 needs it
        )
        
        # Test connection by listing buckets
        s3_client.list_buckets()
        print("✓ Kết nối thành công!\n")
        
    except ClientError as e:
        print(f"✗ Không thể kết nối: {e}")
        print("\nKiểm tra lại:")
        print("  - MinIO server đang chạy?")
        print("  - IP/Port đúng chưa?")
        print("  - Access Key và Secret Key đúng chưa?")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        sys.exit(1)
    
    # Create bucket if not exists
    bucket_name = config['bucket']
    print(f"🪣 Kiểm tra bucket '{bucket_name}'...")
    
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✓ Bucket đã tồn tại\n")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"  Tạo bucket mới...")
            try:
                s3_client.create_bucket(Bucket=bucket_name)
                print(f"✓ Đã tạo bucket '{bucket_name}'\n")
            except ClientError as create_error:
                print(f"✗ Không thể tạo bucket: {create_error}")
                sys.exit(1)
        else:
            print(f"✗ Lỗi kiểm tra bucket: {e}")
            sys.exit(1)
    
    # Upload directories
    print("=" * 50)
    print("Bắt đầu upload artifacts...")
    print("=" * 50)
    print()
    
    upload_directory(s3_client, bucket_name, "whisper_small_xeon", "whisper_small_xeon")
    print()
    upload_directory(s3_client, bucket_name, "whisper_medium_xeon", "whisper_medium_xeon")
    
    print()
    print("=" * 50)
    print("✅ Hoàn tất upload lên MinIO!")
    print("=" * 50)
    print(f"\n🌐 Kiểm tra artifacts tại: {config['endpoint_url']}/{bucket_name}/")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Đã hủy upload")
        sys.exit(1)

