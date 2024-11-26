import random
import json
import torch
import requests
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

FILE = "data.pth"
data = torch.load(FILE, weights_only=True)


input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"
def match_score(pattern, sentence):
    pattern_words = tokenize(pattern)
    matched_words = [word for word in sentence if word in pattern_words]
    return len(matched_words) / len(pattern_words)
def get_response(msg):
    sentence = tokenize(msg)
    matched_intents = []  # Danh sách intent với điểm số khớp

    # Tính điểm khớp cho từng intent
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            score = match_score(pattern, sentence)
            if score > 0.5:  # Ngưỡng khớp
                matched_intents.append((intent, score))

    # Lọc các intent có điểm khớp cao nhất
    if matched_intents:
        matched_intents = sorted(matched_intents, key=lambda x: x[1], reverse=True)
        best_intent = matched_intents[0][0]  # Chọn intent tốt nhất
        return sorted(best_intent['responses'], key=lambda x: calculate_relevance(x, msg), reverse=True)

    # Nếu không tìm thấy intent khớp, gọi API
    print("No matching tag or patterns found, calling Gemini API...")
    return get_gemini_response(msg)

# def get_response(msg):
#     # Tokenize the input message
#     sentence = tokenize(msg)
#     matched_responses = []  # Danh sách các phản hồi khớp

#     for intent in intents['intents']:
#         # Kiểm tra xem có bất kỳ patterns nào trong intent khớp với message không
#         for pattern in intent['patterns']:
#             if any(word in tokenize(pattern) for word in sentence):  # Kiểm tra từ khóa trong patterns
#                 # Sắp xếp các phản hồi dựa trên độ liên quan, sau đó thêm tất cả vào danh sách matched_responses
#                 sorted_responses = sorted(intent['responses'], key=lambda x: calculate_relevance(x, msg), reverse=True)
#                 matched_responses.extend(sorted_responses)

#     # Nếu tìm thấy các phản hồi khớp, trả về tất cả các phản hồi tìm được
#     if matched_responses:
#         print(f"Matching responses from model: {matched_responses}")  # Log các phản hồi khớp
#         return matched_responses

#     # Nếu không tìm thấy bất kỳ match nào, gọi Gemini API
#     print("No matching tag or patterns found, calling Gemini API...")
#     return get_gemini_response(msg)



def calculate_relevance(response, msg):
    # Placeholder for a relevance scoring function
    return sum(1 for word in tokenize(response) if word in tokenize(msg))

def get_gemini_response(msg):
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    api_key = "AIzaSyALw41vjEPzyBrI648d158vSchtjoD23us"  # Thay thế bằng API key của bạn

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": msg  # Message to send to Gemini
                    }
                ]
            }
        ]
    }

    params = {
        "key": api_key
    }

    try:
        # Gửi yêu cầu POST đến Gemini API
        response = requests.post(api_url, headers=headers, params=params, json=data)
        response.raise_for_status()  # Nếu có lỗi HTTP, raise exception

        response_data = response.json()
        
        print(f"Gemini API response: {response_data}")  # Log phản hồi từ Gemini API

        # Trích xuất văn bản từ phản hồi của Gemini
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            content = response_data['candidates'][0].get('content', {})
            parts = content.get('parts', [])
            if parts:
                return parts[0].get('text', 'No text found in Gemini response.')

        return "I couldn't get a response from Gemini."
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")  # Log bất kỳ lỗi nào khi gọi API
        return "There was an error processing your request."

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print(resp)
