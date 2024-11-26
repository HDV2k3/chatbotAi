import threading
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from chat import get_response
import subprocess
import time

app = Flask(__name__)
CORS(app)


@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message")
    print(f"Received message: {message}")  # Log incoming message for debugging

    # Gọi hàm get_response để lấy phản hồi từ mô hình
    response = get_response(message)
    return jsonify({"response": response})

@app.route("/", methods=["GET"])
def index():
    return "Chatbot Server is running!"
def main():
      app.run(host='0.0.0.0', port=5000,debug=True)

# if __name__ == "__main__":
#     app.run(debug=True)
if __name__ == "__main__":
    main()
