# API Test Case Generator from OpenAPI

> Xây dựng công cụ hỗ trợ sinh và thực thi ca kiểm thử chức năng cho REST API dựa trên đặc tả OpenAPI.

## Giới thiệu

Dự án này tập trung xây dựng một công cụ hỗ trợ kiểm thử chức năng cho **REST API**, trong đó:

- **Đầu vào** là file đặc tả **OpenAPI** của hệ thống
- **Đầu ra** là các **ca kiểm thử chức năng được sinh tự động**, kèm khả năng **thực thi** và **tạo báo cáo kết quả**

Công cụ giúp tự động hóa quá trình tạo test case, giảm công sức kiểm thử thủ công, tăng độ bao phủ kiểm thử, đồng thời hỗ trợ đánh giá chất lượng API một cách có hệ thống.

## Bối cảnh đề tài

Trong quá trình phát triển phần mềm, kiểm thử API là một bước quan trọng nhằm bảo đảm các dịch vụ hoạt động đúng với đặc tả. Tuy nhiên, việc thiết kế thủ công toàn bộ ca kiểm thử cho nhiều endpoint thường tốn nhiều thời gian, dễ thiếu sót và khó bảo trì khi hệ thống thay đổi.

OpenAPI là một chuẩn mô tả giao diện cho HTTP API ở dạng máy có thể đọc được, cho phép cả con người lẫn công cụ hiểu được:

- endpoint
- phương thức HTTP
- tham số đầu vào
- request body
- response schema
- các ràng buộc dữ liệu

Từ lợi thế đó, đề tài hướng đến việc khai thác file OpenAPI như một nguồn đầu vào chuẩn để sinh và chạy kiểm thử tự động.

## Mục tiêu đề tài

- Phân tích file đặc tả OpenAPI để trích xuất thông tin cần thiết cho kiểm thử
- Tự động sinh các ca kiểm thử chức năng cho REST API
- Thực thi các ca kiểm thử đã sinh trên hệ thống API mục tiêu
- Kiểm tra và đối chiếu kết quả thực tế với kết quả mong đợi
- Sinh báo cáo kiểm thử theo từng endpoint
- Hỗ trợ đánh giá chất lượng API một cách nhanh chóng và có hệ thống

## Phạm vi chức năng

Công cụ dự kiến hỗ trợ các chức năng chính sau:

### 1. Phân tích đặc tả OpenAPI
Công cụ sẽ đọc file OpenAPI để trích xuất các thành phần như:

- đường dẫn API
- phương thức (`GET`, `POST`, `PUT`, `DELETE`, ...)
- tham số đường dẫn, query, header
- request body
- kiểu dữ liệu
- trường bắt buộc
- enum
- cấu trúc response

### 2. Sinh ca kiểm thử chức năng
Từ dữ liệu đặc tả, hệ thống sẽ sinh các nhóm test case như:

- **Ca hợp lệ**
  - dữ liệu đúng định dạng
  - đủ trường bắt buộc
  - giá trị hợp lệ

- **Ca không hợp lệ**
  - thiếu trường bắt buộc
  - sai kiểu dữ liệu
  - dữ liệu rỗng
  - giá trị vượt biên
  - sai giá trị enum
  - tham số không đúng định dạng

### 3. Thực thi kiểm thử
Sau khi sinh test case, công cụ sẽ:

- gửi request đến API
- nhận phản hồi từ hệ thống
- kiểm tra mã trạng thái HTTP
- đối chiếu dữ liệu phản hồi với schema mong đợi

### 4. Tạo báo cáo kết quả
Kết quả kiểm thử sẽ được tổng hợp thành báo cáo bao gồm:

- tên endpoint
- loại test case
- dữ liệu đầu vào
- kết quả mong đợi
- kết quả thực tế
- trạng thái `Pass/Fail`

## Ý nghĩa của đề tài

Đề tài có ý nghĩa cả về mặt học thuật lẫn thực tiễn:

- Giúp hiểu rõ hơn về kiểm thử chức năng cho API
- Ứng dụng đặc tả OpenAPI vào kiểm thử tự động
- Giảm chi phí và thời gian thiết kế test case thủ công
- Tăng khả năng phát hiện lỗi ở các trường hợp biên và dữ liệu không hợp lệ
- Tạo nền tảng để mở rộng sang các hướng nâng cao như property-based testing hoặc kiểm thử hồi quy

## Hướng tiếp cận triển khai

Dự án có thể được triển khai với các công nghệ sau:

- **Python**: ngôn ngữ chính để xây dựng công cụ
- **Pytest**: framework để tổ chức và thực thi các ca kiểm thử
- **Requests / HTTPX**: gửi request đến API
- **PyYAML / JSON**: đọc và xử lý file OpenAPI
- **Hypothesis** *(tùy chọn)*: hỗ trợ sinh dữ liệu kiểm thử nâng cao theo hướng property-based testing

## Luồng hoạt động dự kiến

```text
OpenAPI Specification
        ↓
Phân tích endpoint, parameter, schema
        ↓
Sinh test case hợp lệ / không hợp lệ
        ↓
Thực thi request đến API
        ↓
So sánh response với expected result
        ↓
Sinh báo cáo Pass/Fail
```

## Kiến trúc đề xuất

```text
project/
├── openapi_parser/        # Phân tích file OpenAPI
├── testcase_generator/    # Sinh test case tự động
├── test_executor/         # Thực thi request và kiểm tra kết quả
├── report_generator/      # Sinh báo cáo kiểm thử
├── sample_specs/          # Chứa file OpenAPI mẫu
├── outputs/               # Kết quả test và báo cáo
└── README.md
```

## Kết quả mong đợi

Sau khi hoàn thành, hệ thống cần đạt được các kết quả sau:

- Đọc và phân tích được file OpenAPI mẫu
- Sinh được bộ test case chức năng cho nhiều endpoint
- Thực thi được các ca kiểm thử đã sinh
- Phát hiện được các trường hợp phản hồi sai đặc tả
- Xuất được báo cáo kết quả rõ ràng, dễ theo dõi

## Hướng phát triển

Trong tương lai, công cụ có thể mở rộng theo các hướng sau:

- hỗ trợ thêm nhiều loại ràng buộc dữ liệu phức tạp
- tích hợp property-based testing
- hỗ trợ kiểm thử bảo mật mức cơ bản
- tích hợp CI/CD để chạy test tự động
- xuất báo cáo HTML trực quan hơn
- hỗ trợ so sánh nhiều phiên bản API

## Kết luận

Đề tài **"Xây dựng công cụ hỗ trợ sinh và thực thi ca kiểm thử chức năng cho REST API dựa trên đặc tả OpenAPI"** là một hướng nghiên cứu và triển khai có tính thực tiễn cao, phù hợp với lĩnh vực **đánh giá và kiểm định chất lượng phần mềm**. Việc tận dụng đặc tả OpenAPI để tự động sinh và chạy kiểm thử không chỉ giúp nâng cao hiệu quả kiểm thử mà còn góp phần chuẩn hóa quá trình đánh giá chất lượng API trong phát triển phần mềm hiện đại.
