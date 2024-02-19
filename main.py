from flask import Flask, request, jsonify
import json
from Oauth2 import *
import re
from database import delete_single_record_from_mysql, get_single_tiktok_info_from_mysql
# Sử dụng hàm
webhook_url = "https://discordapp.com/api/webhooks/1186950849537249361/jEFMfjsioLRm8cIVLBnCuJcPJWepjlXWsqwPCGy131wWq2nQ-6GsO_WR6zcysL2ghvtr"

app = Flask(__name__)

@app.route('/perform_action', methods=['POST'])
def perform_action():
    # Nhận dữ liệu từ yêu cầu POST
    data = request.get_json()
    # Khởi tạo biến result với giá trị mặc định
    result = "Hành động không được thực hiện vì không có dữ liệu"

    # Kiểm tra nếu giá trị được gửi là True, thực hiện một hành động nào đó
    if 'value' in data and data['value'] == True:
        # Thực hiện hành động khi giá trị là True
        if not send_discord_webhook(webhook_url):
            result = "Hành động không thành công vì send_discord_webhook trả về False"
            return jsonify({'result': result}), 400
        else:
            result = "Hành động đã được thực hiện với giá trị là True"
    else:
        # Thực hiện hành động khi giá trị là False
        result = "Không thực hiện hành động vì giá trị là False"
    
    # Trả về kết quả dưới dạng JSON
    return jsonify({'result': result})

def send_discord_webhook(webhook_url):
    try:
        # Xóa toàn bộ tin nhắn trong kênh trước khi gửi tin nhắn mới
        delete_messages_in_channel()
        # Xác thực OAuth và tạo client
        oauth = oauth2_process()
        client = Client(oauth)
        # Lấy thông tin video từ MongoDB
        tiktok_url, tiktok_description = get_single_tiktok_info_from_mysql()
        tiktok_id = re.sub(r'.*?/(\d+)$', r'\1_effect', tiktok_url)
        file_name_to_download = f"{tiktok_id}.mp4"
        # Thư mục lưu trữ video
        folder_video_path = "videos"
        # Đường dẫn đến tệp tin video sau khi tải xuống
        file_path_up_to_discord = os.path.join(folder_video_path, file_name_to_download)
        # Tải xuống tệp tin video từ Box
        download_file_by_name(client, 0, file_name_to_download, folder_video_path)
        def clean():      # Nếu tin nhắn và tệp tin đã được gửi thành công, xóa tệp tin từ thư mục lưu trữ
            os.remove(file_path_up_to_discord)
            delete_file_by_name(client, 0, file_name_to_download)
            delete_single_record_from_mysql()
        # Kiểm tra xem tệp tin video tồn tại không
        if not os.path.exists(file_path_up_to_discord):
            print(f"Tệp tin video '{file_name_to_download}' không tồn tại trong thư mục '{folder_video_path}'.")
            return False
        # Gửi tin nhắn với mô tả đến Discord
        payload_description = {"content": tiktok_description}
        response_description = requests.post(webhook_url, data=json.dumps(payload_description), headers={"Content-Type": "application/json"})
        if response_description.status_code != 204:
            print("Đã xảy ra lỗi khi gửi tin nhắn mô tả. Mã lỗi:", response_description.status_code)
            return False
        
        # Gửi tin nhắn với tệp tin đến Discord
        with open(file_path_up_to_discord, 'rb') as file:
            files = {'file': file}
            payload_url = {"content": tiktok_url}
            response_file = requests.post(webhook_url, files=files, data=payload_url)
            if response_file.status_code != 200:
                print("Đã xảy ra lỗi khi gửi tin nhắn tệp tin. Mã lỗi:", response_file.status_code)
                return False
        clean()
        return True, file_name_to_download
    except Exception as e:
        print("Đã xảy ra lỗi khi gửi tin nhắn:", str(e))
        return False

if __name__ == '__main__':
    app.run()

#scp -r "D:\Project\tiktok" automation@52.249.223.231:/home/automation
