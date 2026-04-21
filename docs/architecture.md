# Architecture Overview

## 1. Mục đích kiến trúc

Kiến trúc của project được thiết kế theo hướng **module hóa vừa đủ**, phù hợp với đồ án cá nhân nhưng vẫn thể hiện được tư duy kỹ thuật rõ ràng của một công cụ kiểm thử phần mềm.

Mục tiêu thiết kế:
- tách trách nhiệm giữa các pha xử lý
- dễ đọc, dễ demo, dễ bảo trì
- không over-engineering
- đủ rõ để mở rộng trong các giai đoạn sau

Pipeline chính:

```text
OpenAPI -> Parser -> Generator -> Executor -> Reporter
```

---

## 2. Các module chính

### 2.1. Parser

**Vai trò:**
- đọc file OpenAPI YAML/JSON
- kiểm tra cấu trúc tối thiểu của tài liệu OpenAPI
- resolve `$ref` nội bộ ở mức cơ bản
- chuẩn hóa dữ liệu thành internal model

**Các thành phần chính:**
- `openapi_loader.py`
- `schema_resolver.py`
- `endpoint_extractor.py`
- `models.py`

**Đầu vào:** file OpenAPI 3.x  
**Đầu ra:** `OpenAPISpecSummary`, `EndpointSpec`, `ResponseSpec`, `RequestBodySpec`, `ApiParameter`

---

### 2.2. Generator

**Vai trò:**
- sinh test case chức năng tự động từ internal model của parser
- tạo dữ liệu mẫu hợp lệ
- sinh một số nhóm invalid case cơ bản

**Nhóm test case hiện có:**
- valid case
- missing required parameter
- missing required field
- wrong data type
- invalid enum
- empty value
- boundary value cơ bản

**Các thành phần chính:**
- `testcase_model.py`
- `valid_case_generator.py`
- `invalid_case_generator.py`
- `boundary_generator.py`
- `testcase_generator.py`

**Đầu vào:** `OpenAPISpecSummary`  
**Đầu ra:** danh sách `GeneratedTestCase`

---

### 2.3. Executor

**Vai trò:**
- build HTTP request từ test case đã sinh
- gửi request thật đến REST API
- thu thập response thực tế
- kiểm tra status code và schema response
- tạo execution result cho từng test case

**Các thành phần chính:**
- `request_builder.py`
- `api_runner.py`
- `response_validator.py`
- `execution_model.py`
- `test_executor.py`

**Đầu vào:** danh sách `GeneratedTestCase`, `base_url`  
**Đầu ra:** `TestExecutionResult`, `TestExecutionSummary`

---

### 2.4. Reporter

**Vai trò:**
- tổng hợp dữ liệu đầu ra từ parser, generator và executor
- sinh report phục vụ demo, báo cáo và lưu trữ kết quả

**Định dạng report hiện có:**
- JSON
- Markdown
- HTML

**Các thành phần chính:**
- `report_model.py`
- `json_reporter.py`
- `markdown_reporter.py`
- `html_reporter.py`
- `report_writer.py`
- `templates/report.html.j2`

**Đầu vào:** spec summary, generation summary, execution summary, execution results  
**Đầu ra:** các file report trong thư mục output

---

### 2.5. Demo API

**Vai trò:**
- cung cấp REST API nhẹ để kiểm chứng executor bằng request thật
- không phụ thuộc hệ thống bên ngoài
- giúp demo end-to-end ổn định

**Công nghệ:** FastAPI  
**Đặc điểm:** in-memory, không database, không auth, validation cơ bản

---

## 3. Luồng dữ liệu end-to-end

### Bước 1. Nhận đầu vào
Người dùng cung cấp:
- file OpenAPI
- `base_url`
- thư mục output

### Bước 2. Parser
Parser đọc tài liệu OpenAPI, resolve `$ref`, trích xuất endpoint và chuyển thành internal model.

### Bước 3. Generator
Generator dùng internal model để sinh ra danh sách test case chức năng tự động.

### Bước 4. Executor
Executor build request từ từng test case, gửi request thật, thu response và kiểm tra status/schema.

### Bước 5. Reporter
Reporter nhận kết quả chạy test và sinh report JSON/Markdown/HTML.

### Bước 6. CLI
CLI điều phối toàn bộ pipeline, in summary ra terminal và hiển thị đường dẫn report đã tạo.

---

## 4. Vai trò của Docker trong hệ thống

Docker được dùng để tăng tính thực tiễn của đề tài theo ba hướng chính:

### 4.1. Chuẩn hóa môi trường chạy
Tool có thể được đóng gói cùng dependency để giảm khác biệt môi trường giữa các máy.

### 4.2. Dễ demo
Docker Compose cho phép bật nhanh:
- `demo-api`
- `tool`

Nhờ vậy, pipeline end-to-end có thể trình bày chỉ với vài lệnh.

### 4.3. Dễ chia sẻ và triển khai thử nghiệm
Người khác clone repo có thể chạy nhanh mà không cần cấu hình lại toàn bộ môi trường Python.

**Lưu ý:** nếu tool chạy trong container nhưng API chạy trên host, `localhost` trong container không phải host machine; cần dùng `host.docker.internal` hoặc cùng network Compose.

---

## 5. Vì sao kiến trúc này phù hợp cho đồ án cá nhân

Kiến trúc này phù hợp vì:
- **đủ sạch để trình bày học thuật**: có module, model, pipeline rõ ràng
- **đủ gọn để hoàn thành bởi một người**: không có thành phần nặng như DB, dashboard hay hệ phân tán phức tạp
- **đủ thực tế để demo**: có request thật, response thật, report thật và Docker
- **dễ mở rộng**: có thể thêm auth, workflow nhiều bước, report nâng cao, CI/CD ở các giai đoạn sau

Nói cách khác, đây là phương án cân bằng giữa:
- phạm vi đồ án cá nhân
- giá trị học thuật
- khả năng demo thực tế

---

## 6. Hạn chế kiến trúc hiện tại

Để giữ đúng mức MVP, kiến trúc hiện tại chưa hỗ trợ sâu:
- auth/security phức tạp
- workflow stateful nhiều bước
- schema phức tạp kiểu `allOf`, `oneOf`, `anyOf`
- async execution
- distributed execution
- lưu lịch sử kết quả bằng database

Đây là hạn chế có chủ đích để ưu tiên hoàn thành một pipeline end-to-end chắc chắn trước.
