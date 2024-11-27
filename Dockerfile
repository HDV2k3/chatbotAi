# Khởi tạo image Python 3.12.3
FROM python:3.12.3

# Cập nhật và cài đặt các gói cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*


# Cài đặt PyTorch với CPU
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install Flask
RUN pip install Flask-Cors
RUN pip install numpy
RUN pip install nltk
RUN pip install schedule
RUN pip install importlib-metadata
RUN pip install requests
RUN pip install urllib3
RUN pip install six
RUN pip install pymongo
# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép toàn bộ ứng dụng vào container
COPY . /app
EXPOSE 5000
# Chạy ứng dụng Flask (hoặc lệnh khởi động của bạn)
CMD ["python", "automation.py"]
