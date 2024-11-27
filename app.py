import threading
import time
import importlib
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from chat import get_response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def run_auto_update():
    while True:
        try:
            logging.info("Đang chạy auto_update_intents...")
            auto_update = importlib.import_module('auto_update_intents')
            auto_update.main()
            time.sleep(3500)
        except Exception as e:
            logging.error(f"Lỗi trong auto_update_intents: {str(e)}")
            time.sleep(60)

def run_training():
    while True:
        try:
            logging.info("Đang chạy training...")
            train = importlib.import_module('train')
            train.main()
            time.sleep(3600)
        except Exception as e:
            logging.error(f"Lỗi trong training: {str(e)}")
            time.sleep(60)

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message")
    response = get_response(message)
    return jsonify({"response": response})

@app.route("/", methods=["GET"])
def index():
    return "Chatbot Server is running!"

def main():
    # Start background tasks
    threading.Thread(target=run_auto_update, daemon=False).start()
    threading.Thread(target=run_training, daemon=False).start()

    # Run Flask in main thread
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
