# Demo Script (3–5 minutes)

Tài liệu này là kịch bản demo ngắn gọn để trình bày đồ án trước giảng viên trong khoảng 3–5 phút.

---

## 1. Mục tiêu phần trình bày

Thông điệp chính cần truyền đạt:
- đề tài sử dụng OpenAPI làm đầu vào để tự động hóa kiểm thử chức năng cho REST API
- công cụ không chỉ phân tích đặc tả mà còn thực thi request thật và sinh report
- Docker giúp demo ổn định, tái lập môi trường và tăng tính thực tiễn của đồ án

---

## 2. Mở đầu (khoảng 30–45 giây)

### Thao tác
Mở repo GitHub hoặc thư mục project và chỉ vào README.

### Lời nói gợi ý
> Đề tài của em là xây dựng một công cụ hỗ trợ sinh và thực thi ca kiểm thử chức năng cho REST API dựa trên đặc tả OpenAPI.  
> Công cụ nhận đầu vào là file OpenAPI, sau đó đi qua 4 bước chính: parse đặc tả, sinh test case, thực thi request thật và xuất report.  
> Mục tiêu là tạo một pipeline tự động, rõ ràng, phù hợp với môn Đánh giá và Kiểm định chất lượng phần mềm.

---

## 3. Giới thiệu kiến trúc (khoảng 40–60 giây)

### Thao tác
Mở `docs/architecture.md` hoặc README phần pipeline.

### Lời nói gợi ý
> Kiến trúc của công cụ được chia thành bốn module chính: Parser, Generator, Executor và Reporter.  
> Parser đọc OpenAPI và chuẩn hóa dữ liệu thành internal model.  
> Generator sinh test case chức năng như valid case, missing required field, wrong data type và boundary value cơ bản.  
> Executor dùng các test case này để gửi HTTP request thật đến API.  
> Cuối cùng Reporter xuất kết quả ra JSON, Markdown và HTML.

---

## 4. Chạy demo API (khoảng 20–30 giây)

### Thao tác
Terminal 1:

```bash
make demo-api
```

hoặc nếu demo bằng Docker Compose:

```bash
make demo-up
```

### Lời nói gợi ý
> Để kiểm chứng executor bằng request thật, em chuẩn bị một demo API rất nhẹ bằng FastAPI.  
> API này không dùng database, chỉ dùng dữ liệu in-memory, nhưng đủ để sinh ra các ca pass và fail thực tế.

---

## 5. Chạy tool end-to-end (khoảng 45–60 giây)

### Thao tác
Terminal 2:

```bash
make run
```

hoặc:

```bash
make demo-run
```

### Lời nói gợi ý
> Khi chạy tool, hệ thống sẽ đọc file OpenAPI mẫu, parse các endpoint, sinh test case tự động, sau đó thực thi HTTP request thật đến API demo.  
> Trên terminal có thể thấy số lượng test case, số lượng pass/fail và preview một số execution results đầu tiên.

---

## 6. Mở report HTML (khoảng 40–60 giây)

### Thao tác
Mở thư mục `reports/` và mở file HTML mới nhất.

### Lời nói gợi ý
> Sau khi chạy xong, công cụ tự động sinh ba loại report: JSON, Markdown và HTML.  
> HTML report phù hợp cho demo vì hiển thị rõ summary, pass/fail, status code kỳ vọng so với thực tế, cùng các lỗi thực thi hoặc validation error nếu có.

### Điểm nên chỉ vào khi mở HTML
- thời gian chạy
- base URL
- total / passed / failed
- một test case PASS
- một test case FAIL
- execution error hoặc validation error nếu có

---

## 7. Nhấn mạnh điểm mạnh (khoảng 30–45 giây)

### Lời nói gợi ý
> Điểm mạnh của đồ án là đã xây được một pipeline end-to-end hoàn chỉnh chứ không chỉ dừng ở mức phân tích đặc tả.  
> Công cụ đã có thể dùng OpenAPI để sinh test case, thực thi request thật, validate kết quả và xuất report.  
> Ngoài ra, Docker và Docker Compose giúp công cụ dễ chạy trên máy khác và dễ trình bày hơn trong bối cảnh thực tế.

---

## 8. Trình bày hạn chế một cách trung thực (khoảng 20–30 giây)

### Lời nói gợi ý
> Hiện tại công cụ mới hỗ trợ OpenAPI 3.x ở mức MVP, chưa xử lý sâu các schema phức tạp như allOf, oneOf, anyOf, và chưa hỗ trợ authentication hoặc workflow nhiều bước.  
> Tuy nhiên, với phạm vi đồ án cá nhân, em ưu tiên hoàn thành chắc chắn một pipeline end-to-end có thể chạy và demo được.

---

## 9. Kết thúc (khoảng 15–20 giây)

### Lời nói gợi ý
> Tóm lại, đồ án này thể hiện cách tận dụng đặc tả OpenAPI để tự động hóa kiểm thử chức năng cho REST API, đồng thời cho thấy tính thực tiễn thông qua request thật, report thật và khả năng đóng gói bằng Docker.

---

## 10. Thứ tự demo ngắn gọn nên nhớ

1. Mở README / giới thiệu đề tài  
2. Giới thiệu pipeline Parser -> Generator -> Executor -> Reporter  
3. Chạy demo API  
4. Chạy tool  
5. Mở report HTML  
6. Nêu điểm mạnh  
7. Nêu hạn chế và hướng phát triển
