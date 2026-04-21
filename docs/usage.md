# Usage Guide

## 1. Môi trường khuyến nghị

- Ubuntu 24.04 LTS
- Python 3.12
- Docker
- Docker Compose

---

## 2. Chuẩn bị môi trường Python

### Tạo virtual environment và cài dependency

```bash
make install
```

Lệnh này sẽ:
- tạo `.venv`
- nâng cấp `pip`
- cài dependency từ `requirements.txt`

---

## 3. Chạy demo API local

```bash
make demo-api
```

Demo API sẽ chạy tại:

```text
http://localhost:8000
```

Endpoint có sẵn:
- `GET /health`
- `GET /users/{userId}`
- `POST /users`

---

## 4. Chạy tool local

Mở terminal khác và chạy:

```bash
make run
```

Hoặc chạy trực tiếp:

```bash
PYTHONPATH=src:. .venv/bin/python main.py \
  --spec samples/sample_openapi.yaml \
  --base-url http://localhost:8000 \
  --output reports
```

---

## 5. Chạy test

```bash
make test
```

Hoặc:

```bash
PYTHONPATH=src:. .venv/bin/pytest -q
```

---

## 6. Chạy bằng Docker

### Build image

```bash
make docker-build
```

### Chạy tool trong container

```bash
make docker-run
```

Trong lệnh này, tool container sẽ gọi API tại:

```text
http://host.docker.internal:8000
```

### Lưu ý quan trọng

Nếu API đang chạy trên host Ubuntu còn tool chạy trong container:
- không nên dùng `http://localhost:8000`
- nên dùng `http://host.docker.internal:8000`

---

## 7. Chạy bằng Docker Compose

### Bật demo API container

```bash
make demo-up
```

### Chạy tool container

```bash
make demo-run
```

Trong Compose, tool gọi API tại:

```text
http://demo-api:8000
```

### Tắt môi trường demo

```bash
make demo-down
```

---

## 8. Đọc kết quả report

Sau khi chạy thành công, thư mục `reports/` sẽ có các file:

- `report_YYYYMMDD_HHMMSS.json`
- `report_YYYYMMDD_HHMMSS.md`
- `report_YYYYMMDD_HHMMSS.html`

### Ý nghĩa từng file

- **JSON**: phù hợp để máy đọc hoặc dùng cho xử lý về sau
- **Markdown**: dễ copy vào README, báo cáo hoặc phụ lục
- **HTML**: dễ mở bằng trình duyệt để demo trước giảng viên

---

## 9. Luồng demo khuyến nghị

### Local demo
1. `make install`
2. `make demo-api`
3. `make run`
4. mở file HTML trong `reports/`

### Docker demo
1. `make demo-up`
2. `make demo-run`
3. mở file HTML trong `reports/`
4. `make demo-down`

---

## 10. Kết quả terminal mong đợi

CLI sẽ hiển thị:
- OpenAPI Summary
- Generated Test Case Summary
- Execution Summary
- Execution Result Preview
- Generated Report Files

Đây là bằng chứng rằng pipeline end-to-end đã chạy thành công.
