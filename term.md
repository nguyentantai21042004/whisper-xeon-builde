## PROPOSAL: Repository Pruning & Documentation Update (Dọn dẹp & Tái cấu trúc Repo)

### 1\. Mục tiêu (Objective)

Loại bỏ toàn bộ mã nguồn thừa, file rác, các ví dụ (examples) và bindings ngôn ngữ không sử dụng (Go, Java, Swift...) ra khỏi repository. Biến `whisper-xeon-builder` thành một repo "tinh gọn", chỉ tập trung vào việc Orchestration (Điều phối) quy trình build và deploy.

### 2\. Tiêu chí Lọc (Filtering Criteria)

Chúng ta sẽ áp dụng chiến lược **"Whitelist"** (Giữ lại cái cần) thay vì "Blacklist" (Xóa cái thừa) để đảm bảo không xóa nhầm file cấu hình quan trọng.

  * **Những thành phần ĐƯỢC GIỮ LẠI (Whitelisted):**
      * `Dockerfile` (File cấu hình build chính).
      * `scripts/` hoặc root: Chứa `push_to_minio.py`.
      * `src/`, `ggml/`, `include/`: Các thư mục Core C++ bắt buộc để compile thư viện (nếu chọn phương án build từ local source).
      * `Makefile` / `CMakeLists.txt`: File hướng dẫn biên dịch.
      * `.github/`: Các workflow CI/CD (nếu có).
  * **Những thành phần SẼ BỊ XÓA (To be deleted):**
      * `bindings/`: Các thư mục code cho iOS, Java, Go, Ruby... (Không dùng đến).
      * `examples/`: Xóa hết, chỉ giữ lại source của `quantize` và `main` (nếu cần test).
      * `tests/`: Các unit test của tác giả gốc (không cần thiết cho quy trình build artifacts).
      * `samples/`: File âm thanh mẫu (gây nặng repo).
      * `models/`: (Nếu có lỡ tải về, xóa đi để tránh commit file nặng lên git).

### 3\. Quy trình Thực thi (Execution Steps)

#### Bước 1: Chạy Script Dọn dẹp (Cleanup Automation)

Tạo một script `maintenance_prune.py` để chạy 1 lần duy nhất trên repo.

**Input:** Cấu trúc thư mục hiện tại của `whisper-xeon-builder`.
**Action:**

1.  Quét toàn bộ thư mục.
2.  So khớp với danh sách Whitelist (Core C++, Build scripts).
3.  Thực hiện lệnh `rm -rf` đối với các folder/file không khớp.
4.  Commit thay đổi: `git commit -m "chore: prune unused sources for xeon builder focus"`.

#### Bước 2: Cập nhật `README.md` (Documentation Overhaul)

File Readme cũ của tác giả (Gerganov) rất dài và không liên quan đến mục đích của bạn. Cần thay thế hoàn toàn bằng nội dung mới.

**Cấu trúc README mới:**

1.  **Title:** Whisper Xeon Builder.
2.  **Project Goal:** "Repository này chuyên dụng để build và đóng gói thư viện Whisper cho môi trường Intel Xeon, tự động đẩy lên MinIO."
3.  **Pipeline Diagram:** Sơ đồ luồng từ Code $\rightarrow$ Docker $\rightarrow$ Artifacts $\rightarrow$ MinIO.
4.  **Usage:**
      * Lệnh build Docker image.
      * Lệnh chạy container để extract artifacts.
      * Hướng dẫn config biến môi trường MinIO.
5.  **Structure:** Giải thích ngắn gọn về output (folder `whisper_small_xeon`, etc.).

### 4\. Kết quả mong đợi (Expected Outcome)

**Before (Trước khi chạy proposal này):**
Repo nặng nề, chứa hàng trăm file code C++, doc tiếng Anh dài dòng, lẫn lộn giữa source code và tool build.

**After (Sau khi chạy):**
Repo sạch sẽ, chỉ còn khoảng 10-20 file/folder thiết yếu. NHƯNG, chắc chắn phải run được Dockerfile và đủ toàn bộ thôn gitn cần thiết.

```text
whisper-xeon-builder/
├── Dockerfile              # Trái tim của repo
├── push_to_minio.py        # Cánh tay nối dài ra Storage
├── README.md               # Hướng dẫn sử dụng (Mới)
├── Makefile                # Build config
├── src/                    # Core Engine (Giữ lại)
├── ggml/                   # Core Tensor Lib (Giữ lại)
└── script/                 # Các script phụ trợ (nếu có)
```
