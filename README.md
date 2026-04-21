# OpenAPI Test Tool

**Đề tài:** *Xây dựng công cụ hỗ trợ sinh và thực thi ca kiểm thử chức năng cho REST API dựa trên đặc tả OpenAPI*

OpenAPI Test Tool là một CLI tool viết bằng Python nhằm tự động hóa quy trình kiểm thử chức năng cho REST API dựa trên đặc tả OpenAPI 3.x. Công cụ đọc file đặc tả, phân tích endpoint, sinh test case chức năng, thực thi HTTP request thật, kiểm tra kết quả response và xuất report phục vụ demo, báo cáo và lưu trữ kết quả.

---

## 1. Mục tiêu của đề tài

Mục tiêu của đồ án là xây dựng một công cụ ở mức MVP nhưng có luồng xử lý đầy đủ:

**OpenAPI -> Parser -> Generator -> Executor -> Reporter**

Công cụ cần đáp ứng các mục tiêu chính:
- đọc file OpenAPI YAML/JSON
- phân tích endpoint, method, parameters, request body và response schema
- sinh test case chức năng tự động
- gửi HTTP request thật đến REST API
- kiểm tra status code và schema response ở mức cơ bản
- xuất report JSON, Markdown và HTML
- chạy được bằng Python local hoặc Docker/Docker Compose

---

## 2. Bài toán mà công cụ giải quyết

Trong thực tế, kiểm thử REST API thường gặp các vấn đề:
- nhiều endpoint, khó test thủ công đầy đủ
- đặc tả OpenAPI có sẵn nhưng chưa được tận dụng để sinh test tự động
- khó duy trì tính nhất quán giữa tài liệu đặc tả và kết quả kiểm thử thực tế
- khó trình bày kết quả kiểm thử rõ ràng nếu chỉ chạy script thô

Công cụ này giải quyết bài toán bằng cách dùng chính đặc tả OpenAPI làm đầu vào trung tâm để:
- chuẩn hóa thông tin API
- sinh test case có hệ thống
- thực thi tự động
- đối chiếu response với kỳ vọng từ đặc tả
- xuất kết quả thành report có thể dùng cho demo và báo cáo

---

## 3. Kiến trúc tổng quan

Pipeline chính của hệ thống:

```text
OpenAPI Spec -> Parser -> Generator -> Executor -> Reporter
```

### Các module chính

- **Parser**
  - đọc YAML/JSON
  - kiểm tra cấu trúc OpenAPI tối thiểu
  - resolve `$ref` cơ bản
  - trích xuất endpoint, parameters, requestBody, responses

- **Generator**
  - sinh valid case và invalid case cơ bản
  - sinh dữ liệu mẫu từ schema
  - hỗ trợ missing required field, wrong type, invalid enum, empty value, boundary cơ bản

- **Executor**
  - build HTTP request từ test case đã sinh
  - gửi request thật bằng `requests`
  - thu response status/body/headers/time
  - validate status code và schema response cơ bản

- **Reporter**
  - tổng hợp kết quả chạy test
  - sinh report JSON, Markdown, HTML

Chi tiết hơn được mô tả trong [docs/architecture.md](docs/architecture.md).

---

## 4. Công nghệ sử dụng

- **Python 3.12**: ngôn ngữ chính của công cụ
- **Typer**: xây dựng CLI
- **Rich**: hiển thị terminal output rõ ràng, dễ demo
- **PyYAML**: đọc file OpenAPI YAML
- **Pydantic**: định nghĩa internal model rõ ràng
- **Requests**: gửi HTTP request đồng bộ
- **jsonschema**: validate response schema cơ bản
- **Jinja2**: render HTML report
- **Pytest**: unit test và smoke test
- **FastAPI**: demo API cục bộ rất nhẹ để kiểm chứng executor
- **Docker / Docker Compose**: đóng gói tool, tái lập môi trường và demo đa dịch vụ

---

## 5. Ý nghĩa thực tiễn của Docker trong đề tài

Docker được dùng có mục đích rõ ràng, không phải chỉ để “có Docker”.

Docker trong đồ án phục vụ các mục tiêu:
- **tái lập môi trường**: giảm khác biệt giữa các máy khi chạy Python tool
- **đóng gói công cụ**: tool có thể chạy mà không cần cài thủ công toàn bộ dependency
- **dễ demo**: có thể chạy cả tool và demo API bằng Docker Compose
- **dễ chia sẻ repo**: người khác clone repo và chạy theo hướng dẫn ngắn gọn hơn

Trong phần demo, Docker Compose cho phép mô phỏng luồng thực tế:
- `tool` container gọi `demo-api` container
- output report được mount ra thư mục host

Lưu ý quan trọng khi demo:
- `localhost` bên trong container **không phải** máy host
- nếu API chạy trên host Ubuntu và tool chạy trong container, nên dùng `host.docker.internal` hoặc cùng network của Docker Compose

---

## 6. Cấu trúc thư mục

```text
openapi-test-tool/
├── .github/
│   └── workflows/
│       └── python-ci.yml
├── demo_api/
│   ├── __init__.py
│   └── app.py
├── docs/
│   ├── architecture.md
│   ├── usage.md
│   └── demo_script.md
├── reports/
│   └── .gitkeep
├── samples/
│   └── sample_openapi.yaml
├── src/
│   └── openapi_test_tool/
│       ├── cli.py
│       ├── config.py
│       ├── parser/
│       ├── generator/
│       ├── executor/
│       ├── reporter/
│       └── utils/
├── tests/
├── Dockerfile
├── Makefile
├── docker-compose.yml
├── main.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## 7. Đầu vào và đầu ra của hệ thống

### Đầu vào
- file OpenAPI 3.x (`.yaml`, `.yml`, `.json`)
- `base_url` của REST API đích
- thư mục output để lưu report

### Đầu ra
- terminal summary
- report JSON
- report Markdown
- report HTML

Tên file report theo timestamp:
- `report_YYYYMMDD_HHMMSS.json`
- `report_YYYYMMDD_HHMMSS.md`
- `report_YYYYMMDD_HHMMSS.html`

---

## 8. Cài đặt và chạy local trên Ubuntu 24.04 LTS

### Yêu cầu
- Ubuntu 24.04 LTS
- Python 3.12
- Docker và Docker Compose (nếu muốn demo bằng container)

### Cài dependency

```bash
make install
```

### Chạy demo API local

```bash
make demo-api
```

Demo API chạy tại:

```text
http://localhost:8000
```

### Chạy tool local

Mở terminal khác:

```bash
make run
```

Hoặc:

```bash
PYTHONPATH=src:. .venv/bin/python main.py \
  --spec samples/sample_openapi.yaml \
  --base-url http://localhost:8000 \
  --output reports
```

---

## 9. Chạy bằng Docker

### Build image

```bash
make docker-build
```

### Chạy tool trong Docker để gọi API trên host

```bash
make docker-run
```

Cách này dùng:

```text
http://host.docker.internal:8000
```

---

## 10. Chạy demo bằng Docker Compose

### Bật demo API container

```bash
make demo-up
```

### Chạy tool container

```bash
make demo-run
```

Tool sẽ gọi API qua network nội bộ của Compose tại:

```text
http://demo-api:8000
```

### Tắt môi trường demo

```bash
make demo-down
```

---

## 11. Chạy test

```bash
make test
```

Hoặc:

```bash
PYTHONPATH=src:. .venv/bin/pytest -q
```

Nếu bật GitHub Actions, workflow cũng sẽ tự chạy `pytest` khi push hoặc pull request.

---

## 12. Kết quả đầu ra mong đợi

Khi chạy thành công, CLI sẽ hiển thị:
- OpenAPI summary
- Generated test case summary
- Execution summary
- Preview một số execution results
- Danh sách file report đã tạo

Thư mục `reports/` sẽ chứa:
- file JSON để máy đọc và mở rộng về sau
- file Markdown để chèn vào README hoặc báo cáo
- file HTML để demo trực quan trước giảng viên

---

## 13. Tính năng hiện tại

Hiện tại project đã hỗ trợ:
- parse OpenAPI 3.x ở mức MVP
- resolve `$ref` nội bộ trong `components/schemas`
- sinh test case chức năng cơ bản
- thực thi HTTP request thật
- validate status code
- validate response schema JSON cơ bản
- sinh report JSON / Markdown / HTML
- demo API cục bộ bằng FastAPI
- chạy local hoặc bằng Docker/Docker Compose
- unit test và smoke test tự động

---

## 14. Limitations

Các hạn chế hiện tại được giữ minh bạch để đúng mức đồ án cá nhân:
- mới hỗ trợ OpenAPI 3.x ở mức cơ bản
- chưa hỗ trợ sâu `allOf`, `oneOf`, `anyOf`
- chưa hỗ trợ auth/security phức tạp
- chưa hỗ trợ workflow phụ thuộc nhiều bước giữa các endpoint
- chưa hỗ trợ async execution hoặc performance testing
- schema validation mới ở mức thực dụng, chưa bao phủ toàn bộ chuẩn OpenAPI/JSON Schema
- chưa có dashboard web hoặc lưu lịch sử bằng database

---

## 15. Future work

Các hướng phát triển tiếp theo có thể gồm:
- hỗ trợ Bearer token / API key / OAuth cơ bản
- sinh dữ liệu test nâng cao hơn
- hỗ trợ dependency giữa các endpoint
- mở rộng schema validation cho `allOf`, `oneOf`, `anyOf`
- xuất thêm JUnit/XML cho CI
- tích hợp CI/CD sâu hơn
- thêm filter theo tag, path, method
- hỗ trợ chạy song song

---

## 16. Tài liệu bổ sung

- [Kiến trúc hệ thống](docs/architecture.md)
- [Hướng dẫn sử dụng](docs/usage.md)
- [Kịch bản demo 3-5 phút](docs/demo_script.md)

---

## 17. Trạng thái repo

Repo hiện phù hợp để:
- nộp đồ án môn học
- demo trước giảng viên
- đẩy lên GitHub với cấu trúc rõ ràng
- tiếp tục mở rộng ở các giai đoạn sau
