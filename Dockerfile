# Sử dụng image Python mới nhất (hoặc phiên bản cụ thể bạn cần)
FROM python:latest

# Cài đặt môi trường làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt tất cả các thư viện Python từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép tất cả các tệp trong thư mục hiện tại vào container
COPY . .

# Lệnh chạy khi container khởi động
CMD ["python", "automation.py"]
