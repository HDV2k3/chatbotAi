import json
import torch
import requests
from model import NeuralNet
from nltk_utils import  tokenize
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
load_dotenv()
# URI kết nối tới MongoDB Atlas
urlDatabase = os.getenv('URL_DATABASE')

# Tạo một client mới và kết nối đến MongoDB Atlas
client = MongoClient(urlDatabase, server_api=ServerApi('1'))

def get_db():
    """
    Kết nối đến cơ sở dữ liệu MongoDB và trả về đối tượng cơ sở dữ liệu.
    """
    # Kết nối đến database 'intents'
    db = client.get_database()  # Kết nối đến database đã chỉ định trong URI (không cần phải chỉ định lại tên 'intents' ở đây)
    return db

# Lấy collection 'intents' từ MongoDB
def get_intents_collection():
    db = get_db()  # Lấy database
    return db['intents']  # Trả về collection 'intents'

# Thiết lập thiết bị (GPU nếu có, nếu không sẽ sử dụng CPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Đọc dữ liệu intents từ tệp intents.json
with open('intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

# Đường dẫn tới tệp mô hình đã được huấn luyện
FILE = "data.pth"
data = torch.load(FILE, weights_only=True)

# Tải thông tin từ mô hình đã huấn luyện
input_size = data["input_size"]  # Kích thước đầu vào
hidden_size = data["hidden_size"]  # Số lượng neuron trong lớp ẩn
output_size = data["output_size"]  # Kích thước đầu ra
all_words = data['all_words']  # Từ vựng của mô hình
tags = data['tags']  # Các nhãn (tags) trong intents
model_state = data["model_state"]  # Trạng thái mô hình đã được lưu

# Khởi tạo mô hình và tải trạng thái mô hình đã lưu
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()  # Chuyển mô hình sang chế độ đánh giá (evaluation mode)

# Tên bot
bot_name = "Sam"

# Hàm tính điểm khớp giữa câu nhập và mẫu trong intents
def match_score(pattern, sentence):
    """
    Tính toán tỷ lệ khớp giữa câu mẫu và câu người dùng.
    pattern: mẫu từ intent.
    sentence: câu nhập từ người dùng.
    """
    pattern_words = tokenize(pattern)  # Tách từ của mẫu
    matched_words = [word for word in sentence if word in pattern_words]  # Các từ khớp
    return len(matched_words) / len(pattern_words)  # Tỷ lệ khớp

def get_response(msg):
    """
    Nhận phản hồi từ chatbot dựa trên câu nhập của người dùng.
    Nếu không có intent khớp, lưu câu hỏi vào tệp JSON, sau đó gọi API Gemini để xử lý.
    """
    sentence = tokenize(msg)  # Tách từ của câu nhập
    matched_intents = []  # Danh sách intent khớp với điểm số

    # Duyệt qua các intents để tính điểm khớp
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            score = match_score(pattern, sentence)
            if score > 0.5:  # Nếu điểm khớp vượt ngưỡng 0.5
                matched_intents.append((intent, score))

    # Chọn intent có điểm khớp cao nhất
    if matched_intents:
        matched_intents = sorted(matched_intents, key=lambda x: x[1], reverse=True)
        best_intent = matched_intents[0][0]  # Lấy intent khớp tốt nhất
        
        # Trả về tất cả các responses của intent phù hợp
        responses = best_intent['responses']
        # Nối tất cả các phản hồi lại với nhau và thêm câu hỏi bổ sung
        response_text = "\n".join(responses) + "\n\nBạn còn câu hỏi nào cho tôi không?"
        return response_text

  
    gemini_response = get_gemini_response(msg)  # Gọi API Gemini
      # Nếu không tìm thấy intent phù hợp, lưu câu hỏi và gọi API Gemini
    print("No matching tag or patterns found, saving to unresolved intents...")
    save_unresolved_intent_to_file(msg,gemini_response)  # Lưu câu hỏi chưa giải quyết
    return f"{gemini_response}\n\nBạn còn câu hỏi nào cho tôi không?"

def save_unresolved_intent_to_file(new_question,responses):
    """
    Lưu câu hỏi chưa được giải quyết vào tệp intents.json với định dạng chuẩn.
    """
    file_path = 'intents.json'

    # Kiểm tra nếu tệp tồn tại, nếu không, tạo mới
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({"intents": []}, f, ensure_ascii=False, indent=4)

    # Đọc nội dung hiện tại từ tệp
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Tạo một intent mới với tag là 'chưa xác định' và câu hỏi chưa được giải quyết
    new_intent = {
        "tag": "chưa xác định",  # Tag cố định cho câu hỏi chưa xác định
        "patterns": [new_question],  # Câu hỏi chưa giải quyết
        "responses": [responses]  # Phản hồi Gemini
    }

    # Thêm intent mới vào danh sách intents
    data['intents'].append(new_intent)

    # Ghi lại dữ liệu vào tệp
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Unresolved intent saved json: {new_intent}")
    save_intent_to_mongo(new_intent)
    print(f"Unresolved intent saved database: {new_intent}")
# Hàm tính độ liên quan giữa phản hồi và câu nhập của người dùng
def save_intent_to_mongo(new_intent):
    """
    Lưu intent vào MongoDB collection 'intents'.
    new_intent: Dữ liệu intent cần lưu.
    """
    collection = get_intents_collection()  # Lấy collection 'intents'
    
    # Insert intent_data vào collection
    result = collection.insert_one(new_intent)
    print(f"Intent saved with id: {result.inserted_id}")
def calculate_relevance(response, msg):
    """
    Tính độ liên quan giữa câu trả lời và câu nhập của người dùng.
    response: phản hồi tiềm năng.
    msg: câu nhập của người dùng.
    """
    return sum(1 for word in tokenize(response) if word in tokenize(msg))

# Hàm gọi API Gemini để tạo phản hồi
def get_gemini_response(msg):
    """
    Gọi API Gemini để tạo phản hồi khi không tìm được intent phù hợp.
    msg: câu nhập từ người dùng.
    """
    api_url = os.getenv('API_URL')
    api_key = os.getenv('API_KEY')

    # Headers cho yêu cầu HTTP
    headers = {
        'Content-Type': 'application/json',
    }

    # Dữ liệu gửi trong yêu cầu POST
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": msg  # Nội dung cần gửi tới API
                    }
                ]
            }
        ]
    }

    # Tham số URL
    params = {
        "key": api_key
    }

    try:
        # Gửi yêu cầu POST đến API
        response = requests.post(api_url, headers=headers, params=params, json=data)
        response.raise_for_status()  # Kiểm tra lỗi HTTP (nếu có)

        response_data = response.json()
        
        print(f"Gemini API response: {response_data}")  # Log phản hồi từ API

        # Trích xuất nội dung từ phản hồi của API
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            content = response_data['candidates'][0].get('content', {})
            parts = content.get('parts', [])
            if parts:
                return parts[0].get('text', 'No text found in Gemini response.')

        return "I couldn't get a response from Gemini."
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")  # Log lỗi gọi API
        return "There was an error processing your request."
# Kết nối với MongoDB

# Hàm chính cho chatbot
if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")  # Nhận câu nhập từ người dùng
        if sentence == "quit":  # Thoát nếu người dùng nhập 'quit'
            break

        resp = get_response(sentence)  # Lấy phản hồi từ chatbot
        print(resp)

