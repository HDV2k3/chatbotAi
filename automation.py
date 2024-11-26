import threading
import time
import schedule
from datetime import datetime
import importlib
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),  # Log to file with UTF-8 encoding
        logging.StreamHandler()  # Log to console
    ]
)


def run_auto_update():
    """Hàm chạy auto_update_intents"""
    while True:
        try:
            logging.info("Đang chạy auto_update_intents...")
            auto_update = importlib.import_module('auto_update_intents')
            auto_update.main()  # Giả sử có hàm main() trong file
            time.sleep(3500)  # Đợi 5 phút trước khi chạy lại
        except Exception as e:
            logging.error(f"Lỗi trong auto_update_intents: {str(e)}")
            time.sleep(60)  # Đợi 1 phút nếu có lỗi

def run_training():
    """Hàm chạy train.py"""
    while True:
        try:
            logging.info("Đang chạy training...")
            train = importlib.import_module('train')
            train.main()  # Giả sử có hàm main() trong file
            time.sleep(3600)  # Đợi 10 phút trước khi train lại
        except Exception as e:
            logging.error(f"Lỗi trong training: {str(e)}")
            time.sleep(60)

def main():
    # Tạo và start thread cho auto_update_intents
    auto_update_thread = threading.Thread(target=run_auto_update, daemon=True)
    auto_update_thread.start()
    logging.info("Đã start thread auto_update_intents")

    # Tạo và start thread cho training
    training_thread = threading.Thread(target=run_training, daemon=True)
    training_thread.start()
    logging.info("Đã start thread training")

    # Import và chạy app.py trong thread chính
    try:
        logging.info("Đang khởi động app chính...")
        app = importlib.import_module('app')
        app.main()  # Giả sử có hàm main() trong file app.py
    except Exception as e:
        logging.error(f"Lỗi trong app chính: {str(e)}")

if __name__ == "__main__":
    main()