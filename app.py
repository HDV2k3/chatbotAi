from flask import Flask, request, jsonify
from flask_cors import CORS
from chat import get_response

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

if __name__ == "__main__":
    app.run(debug=True)