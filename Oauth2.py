from boxsdk import Client, OAuth2
import os
import requests
from datetime import datetime
import pytz


saved_access_token = None
saved_refresh_token = None
def load_tokens_from_file():
    global saved_access_token
    global saved_refresh_token
    # Load tokens từ tệp tin nếu có
    if os.path.exists('tokens.txt'):
        with open('tokens.txt', 'r') as file:
            tokens = file.readlines()
            saved_access_token = tokens[0].strip()
            saved_refresh_token = tokens[1].strip()

def store_tokens_to_file(access_token, refresh_token):
    # Lưu tokens vào tệp tin
    with open('tokens.txt', 'w') as file:
        file.write(access_token + '\n')
        file.write(refresh_token + '\n')

def oauth2_process():
    global saved_access_token
    global saved_refresh_token

    load_tokens_from_file()

    # Nếu đã có tokens, sử dụng chúng
    if saved_access_token and saved_refresh_token:
        oauth = OAuth2(
            client_id='lj0iuv31t35gm3id4rsvewaa7wfy83sd',
            client_secret='JpH5pdqfce1V0g8LP42rwHdcuinPxLg0',
            access_token=saved_access_token,
            refresh_token=saved_refresh_token,
            store_tokens=store_tokens_to_file,
        )
    else:
        # Nếu không có tokens, yêu cầu xác thực từ người dùng
        oauth = OAuth2(
            client_id='lj0iuv31t35gm3id4rsvewaa7wfy83sd',
            client_secret='JpH5pdqfce1V0g8LP42rwHdcuinPxLg0',
            store_tokens=store_tokens_to_file,
        )

        auth_url, csrf_token = oauth.get_authorization_url('https://app.box.com/oauth2/callback')
        print(auth_url)

        # Người dùng nhập authorization code sau khi xác thực thành công
        authorization_code = input("Nhập authorization code từ URL redirect sau khi xác thực thành công: ")
        code = authorization_code.split('code=')[1]

        access_token, refresh_token = oauth.authenticate(code)
        store_tokens_to_file(access_token, refresh_token)

    return oauth











def download_file_by_name(client, folder_id, file_name, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created directory: {output_directory}")

    items = client.folder(folder_id).get_items()

    for item in items:
        if item.name == file_name:
            try:
                output_path = os.path.join(output_directory, item.name)
                with open(output_path, 'wb') as file_output:
                    file_content = client.file(file_id=item.id).content()
                    file_output.write(file_content)
                # print(f"Downloaded {file_name} successfully to {output_directory}")
                return True
            except Exception as e:
                print(f"Error downloading {file_name}: {e}")
                return False
    print(f"File {file_name} not found in Box.")
    return False

def delete_file_by_name(client, folder_id, file_name):
    items = client.folder(folder_id).get_items()
    
    for item in items:
        if item.name == file_name:
            try:
                client.file(file_id=item.id).delete()
                # print(f"Deleted {file_name} successfully")
                return True
            except Exception as e:
                print(f"Error deleting {file_name}: {e}")
                return False

def get_single_tiktok_info(file_path):
    url = ''
    description = ''

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

            for line in lines:
                line = line.strip()
                if line.startswith('URL TikTok:'):
                    url = line.replace('URL TikTok: ', '')
                elif line.startswith('Description:'):
                    description = line.replace('Description: ', '')
                    break  # Dừng sau khi đã tìm thấy một cặp URL và mô tả

    except Exception as e:
        print(f"An error occurred while reading the file: {str(e)}")
    
    return url, description


def delete(ten_file):
    try:
        deleted_content = []  # Initialize a list to store deleted content
        with open(ten_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

            # Store the content to be deleted
            deleted_content = lines[:3]

        with open(ten_file, 'w', encoding='utf-8') as file:
            for index, line in enumerate(lines):
                if index < 3:
                    continue
                file.write(line)

        # Construct URL and description of deleted content
        deleted_description = ''.join(deleted_content)
        return f"\nĐã xóa:\n{deleted_description}"
    
    except FileNotFoundError:
        return "File không tồn tại"
    except Exception as e:
        return f"Lỗi: {str(e)}"
    
def send_message(webhook_url, file_path, description):

    # Mở file để đọc dữ liệu
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    # Tạo nội dung tin nhắn
    message = f'{description}'
    
    # Tạo payload để gửi
    payload = {'content': message}
    
    
    # Gửi yêu cầu POST với multipart/form-data
    response = requests.post(webhook_url, data=payload)
    
    return response.text  
    
def send_message_with_file(webhook_url, file_path, url_tikok, date_time):

    # Mở file để đọc dữ liệu
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    # Tạo nội dung tin nhắn
    message = f'{date_time}\n{url_tikok}'
    
    # Tạo payload để gửi
    payload = {'content': message}
    
    # Thêm file vào payload với key là 'file' và giá trị là dữ liệu của file
    files = {'file': (file_path, file_data)}
    
    # Gửi yêu cầu POST với multipart/form-data
    response = requests.post(webhook_url, data=payload, files=files)
    
    return response.text

def delete_file_in_folder(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            # print(f"Đã xóa tệp {file_path} thành công")
        else:
            print(f"Tệp {file_path} không tồn tại")
    except Exception as e:
        print(f"Lỗi: {str(e)} khi xóa tệp {file_path}")



def current_time_with_format():
    # Lấy thời gian hiện tại ở múi giờ UTC
    now_utc = datetime.utcnow()

    # Chuyển đổi múi giờ từ UTC sang múi giờ Việt Nam (UTC+7)
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    time_vietnam = pytz.utc.localize(now_utc).astimezone(vn_tz)

    # Định dạng thời gian với năm đầy đủ (yyyy)
    formatted_time = time_vietnam.strftime("Time: %H:%M:%S\nDate: %d/%m/%Y ")

    # Trả về thời gian hiện tại ở múi giờ Việt Nam
    return formatted_time