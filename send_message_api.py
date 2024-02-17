from flask import Flask, request, jsonify
import requests
import json
from Oauth2 import *
import re
# Sử dụng hàm
webhook_url = "https://discordapp.com/api/webhooks/1186950849537249361/jEFMfjsioLRm8cIVLBnCuJcPJWepjlXWsqwPCGy131wWq2nQ-6GsO_WR6zcysL2ghvtr"
message = "Xin chào từ Webhook Discord!"

app = Flask(__name__)

@app.route('/perform_action', methods=['POST'])
def perform_action():
    # Nhận dữ liệu từ yêu cầu POST
    data = request.get_json()
    
    # Khởi tạo biến result với giá trị mặc định
    result = "Hành động không được thực hiện vì không có dữ liệu"

    # Kiểm tra nếu giá trị được gửi là True, thực hiện một hành động nào đó
    if data['value'] == True:
        # Thực hiện hành động khi giá trị là True
        send_discord_webhook(webhook_url)
        result = "Hành động đã được thực hiện với giá trị là True"
    else:
        # Thực hiện hành động khi giá trị là False
        result = "Không thực hiện hành động vì giá trị là False"
    
    # Trả về kết quả dưới dạng JSON
    return jsonify({'result': result})



def process_video_data():
    oauth = oauth2_process()
    client = Client(oauth)
    input_folder_name = "ugckieulinh"
    file_path = f"videos/description/{input_folder_name}_description.txt"
    
    folder_video_path = "videos/videos"
    tiktok_url, tiktok_description = get_single_tiktok_info(file_path)
    box_folder_id = "0"
    tiktok_id = re.sub(r'.*?/(\d+)$', r'\1_effect', tiktok_url)
    file_name_to_download = f"{tiktok_id}.mp4"
    file_path_up_to_discord = f"videos/videos/{file_name_to_download}"
    download_file_by_name(client, box_folder_id, file_name_to_download, folder_video_path)
    
    return file_path_up_to_discord, tiktok_description, tiktok_url, file_path

def send_discord_webhook(webhook_url):
    try:
        delete_messages_in_channel()
        file_path_up_to_discord, tiktok_description, tiktok_url, file_path = process_video_data()
        payload = {"content": tiktok_description}
        response = requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        send_message_with_file(webhook_url, file_path_up_to_discord, tiktok_url)
        delete_file_in_folder(file_path_up_to_discord)
        delete(file_path)

        if response.status_code == 204:
            print("Tin nhắn đã được gửi thành công!")
            return True
        else:
            print("Đã xảy ra lỗi khi gửi tin nhắn. Mã lỗi:", response.status_code)
            return False
    except Exception as e:
        print("Đã xảy ra lỗi khi gửi tin nhắn:", str(e))
        return False





if __name__ == '__main__':
    app.run()

#scp -r "D:\Project\tiktok" automation@52.249.223.231:/home/automation
