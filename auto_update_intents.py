import json
import requests
import time
import os
import logging
# Đường dẫn đến file intents.json
intents_file = 'intents.json'

# Hàm gọi API để lấy dữ liệu từ bất kỳ API nào
def get_data_from_api(url):
    try:
        print(f"Đang gọi API: {url}")  # Thêm thông báo log
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['responseCode'] == 101000:
                print(f"API {url} trả về dữ liệu hợp lệ.")
                return data['data']['intents']  # Trả về intents từ API
            else:
                print(f"Error: API {url} không trả về dữ liệu hợp lệ, mã phản hồi: {data['responseCode']}.")
                return []
        else:
            print(f"Error: API {url} trả về mã lỗi {response.status_code}.")
            return []
    except Exception as e:
        print(f"Exception when calling API {url}: {e}")
        return []

# Hàm đọc intents.json và thêm dữ liệu mới vào
def update_intents_with_rooms():
    # Định nghĩa các API để lấy dữ liệu
    api_urls = [
        "http://localhost:8080/marketing/train/roomInfoName",
        "http://localhost:8080/marketing/train/address",
        # Thêm các API khác vào đây
    ]

    intents = {'intents': []}

    # Kiểm tra file intents.json, nếu không tồn tại hoặc trống thì khởi tạo cấu trúc rỗng
    if os.path.exists(intents_file) and os.stat(intents_file).st_size > 0:
        try:
            with open(intents_file, 'r', encoding='utf-8') as f:
                intents = json.load(f)
                print(f"Đã đọc file {intents_file}.")  # Thêm thông báo log
        except json.JSONDecodeError:
            print(f"Lỗi định dạng JSON trong file {intents_file}. Khởi tạo lại file.")
            intents = {'intents': []}

    # Sao chép intents hiện tại để so sánh sau này
    original_intents = json.loads(json.dumps(intents))  # Sao chép chính xác

    # Hàm để cập nhật hoặc thêm intent mới vào
    def add_or_update_intent(tag, patterns, responses):
        # Tìm intent với tag đã tồn tại
        existing_tag = next((item for item in intents['intents'] if item['tag'] == tag), None)
        if existing_tag:
            # Nếu tag đã tồn tại, cập nhật patterns và responses (loại bỏ trùng lặp)
            existing_tag['patterns'] = list(set(existing_tag['patterns']).union(patterns))
            existing_tag['responses'] = list(set(existing_tag['responses']).union(responses))
        else:
            # Nếu tag chưa có, tạo mới
            intents['intents'].append({
                'tag': tag,
                'patterns': list(set(patterns)),  # Loại bỏ trùng lặp trong patterns mới
                'responses': list(set(responses))  # Loại bỏ trùng lặp trong responses mới
            })

    # Lấy dữ liệu từ tất cả các API
    for url in api_urls:
        data = get_data_from_api(url)
        if data:  # Nếu có dữ liệu từ API
            for intent in data:
                add_or_update_intent(intent['tag'], intent['patterns'], intent['responses'])

    # Kiểm tra xem dữ liệu có thay đổi không
    if intents != original_intents:
        # Lưu lại intents.json sau khi cập nhật
        try:
            with open(intents_file, 'w', encoding='utf-8') as f:
                json.dump(intents, f, ensure_ascii=False, indent=4)
            print(f"File {intents_file} đã được cập nhật.")
        except Exception as e:
            print(f"Lỗi khi ghi file {intents_file}: {e}")
    else:
        print("Không có thay đổi trong dữ liệu. Không cập nhật file.")

# if __name__ == "__main__":
#     update_intents_with_rooms()  

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Starting update intents process...")
    update_intents_with_rooms()  
    logging.info("update process complete.")

if __name__ == "__main__":
    main()
