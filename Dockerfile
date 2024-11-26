# Bắt đầu từ image python:3.9-slim
FROM python:3.12.3

# Cập nhật và cài đặt các gói cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các thư viện Python cần thiết
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install numpy
RUN pip install nltk
RUN pip install flask
RUN pip install flask-cors
RUN pip install schedule
RUN pip install importlib-metadata
# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép ứng dụng vào container
COPY . /app

# Chạy ứng dụng Flask (hoặc lệnh khởi động của bạn)
CMD ["python", "automation.py"]
