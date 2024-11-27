import json
import torch
import requests
from model import NeuralNet
from nltk_utils import  tokenize
import os 
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

# # Hàm xử lý phản hồi từ chatbot
# def get_response(msg):
#     """
#     Nhận phản hồi từ chatbot dựa trên câu nhập của người dùng.
#     Nếu không có intent khớp, gọi API Gemini để xử lý.
#     """
#     sentence = tokenize(msg)  # Tách từ của câu nhập
#     matched_intents = []  # Danh sách intent khớp với điểm số

#     # Duyệt qua các intents để tính điểm khớp
#     for intent in intents['intents']:
#         for pattern in intent['patterns']:
#             score = match_score(pattern, sentence)
#             if score > 0.5:  # Nếu điểm khớp vượt ngưỡng 0.5
#                 matched_intents.append((intent, score))

#     # Chọn intent có điểm khớp cao nhất
#     if matched_intents:
#         matched_intents = sorted(matched_intents, key=lambda x: x[1], reverse=True)
#         best_intent = matched_intents[0][0]  # Lấy intent khớp tốt nhất
#         return sorted(best_intent['responses'], key=lambda x: calculate_relevance(x, msg), reverse=True)

#     # Nếu không tìm thấy intent phù hợp, gọi API Gemini
#     print("No matching tag or patterns found, calling Gemini API...")
#     return get_gemini_response(msg)
def get_response(msg):
    """
    Nhận phản hồi từ chatbot dựa trên câu nhập của người dùng.
    Nếu không có intent khớp, câu hỏi sẽ được lưu vào tệp JSON để phân tích sau.
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

        # Lấy phản hồi phù hợp nhất và thêm câu hỏi bổ sung
        response = sorted(
            best_intent['responses'], 
            key=lambda x: calculate_relevance(x, msg), 
            reverse=True
        )[0]
        return f"{response}\n\nBạn còn câu hỏi nào muốn hỏi tôi nữa không? Tôi sẵn sàng trả lời những gì tôi biết."

    # Nếu không tìm thấy intent phù hợp, lưu câu hỏi vào tệp JSON
    print("No matching tag or patterns found, saving to unresolved intents...")

    # Tạo intent mới với thông tin cơ bản
    unresolved_intent = {
        "tag": f"unresolved_{len(intents['intents']) + 1}",
        "patterns": [msg],
        "responses": []
    }

    # Thêm intent này vào danh sách intents
    intents['intents'].append(unresolved_intent)

    # Ghi vào tệp JSON
    save_unresolved_intent_to_file(unresolved_intent)

    # Gọi API Gemini như một phương án cuối
    gemini_response = get_gemini_response(msg)
    return f"{gemini_response}\n\nBạn còn câu hỏi nào muốn hỏi tôi nữa không? Tôi sẵn sàng trả lời những gì tôi biết."

def save_unresolved_intent_to_file(new_intent):
    """
    Lưu intent chưa được giải quyết vào tệp intents.json.
    """
    file_path = 'intents.json'

    # Kiểm tra nếu tệp tồn tại, nếu không, tạo mới
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({"intents": []}, f, ensure_ascii=False, indent=4)

    # Đọc nội dung hiện tại từ tệp
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Thêm intent mới vào danh sách intents
    data['intents'].append(new_intent)

    # Ghi lại dữ liệu vào tệp
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Unresolved intent saved: {new_intent}")
# Hàm tính độ liên quan giữa phản hồi và câu nhập của người dùng
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
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    api_key = "AIzaSyALw41vjEPzyBrI648d158vSchtjoD23us"  # API key (cần bảo mật hơn)

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

# Hàm chính cho chatbot
if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")  # Nhận câu nhập từ người dùng
        if sentence == "quit":  # Thoát nếu người dùng nhập 'quit'
            break

        resp = get_response(sentence)  # Lấy phản hồi từ chatbot
        print(resp)
