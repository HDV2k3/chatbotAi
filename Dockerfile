# Sử dụng image Python mới nhất (hoặc phiên bản cụ thể bạn cần)
FROM python:latest

# Cài đặt môi trường làm việc trong container
WORKDIR /app

# Cài đặt các thư viện cần thiết cho việc xây dựng ứng dụng (như build-essential, libpq-dev nếu cần)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt tất cả các thư viện Python từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép tất cả các tệp trong thư mục hiện tại vào container
COPY . .

# Lệnh chạy khi container khởi động
CMD ["python", "automation.py"]
