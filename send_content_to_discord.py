import re
import requests
from Oauth2 import *

input_folder_name = "_dun.hen16"
file_path = f"/home/thanhnam/Desktop/Tiktok/videos/description/{input_folder_name}_description.txt"


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
                print(f"Downloaded {file_name} successfully to {output_directory}")
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
                print(f"Deleted {file_name} successfully")
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
    
def send_message_with_file(webhook_url, file_path, url_tikok, description):
    c = "----------------------------------------"
    # Mở file để đọc dữ liệu
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    # Tạo nội dung tin nhắn
    message = f'{c}\n{url_tikok}\n\n{description}'
    
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
            print(f"Đã xóa tệp {file_path} thành công")
        else:
            print(f"Tệp {file_path} không tồn tại")
    except Exception as e:
        print(f"Lỗi: {str(e)} khi xóa tệp {file_path}")

def main():
    oauth = oauth2_process()
    client = Client(oauth)
    webhook_url = 'https://discordapp.com/api/webhooks/1185107643145134090/5HgKD6JC_fpKRdFuHWOmESzcn4t7GRvbnEuTfqef4mQqJjEdj77xjncMPmy8ssiW-tiW'

    folder_description_path = f"/home/thanhnam/Desktop/Tiktok/videos/description"
    box_folder_id = "0"
    file_descreption_to_download = f"{input_folder_name}_description.txt"
    folder_video_path = "/home/thanhnam/Desktop/Tiktok/videos/videos"

    download_file_by_name(client, box_folder_id, file_descreption_to_download, folder_description_path)
    delete_file_by_name(client, box_folder_id, file_descreption_to_download)

    tiktok_url, tiktok_description = get_single_tiktok_info(file_path)
    tiktok_id = re.sub(r'.*?/(\d+)$', r'\1_effect', tiktok_url)
    file_name_to_download = f"{tiktok_id}.mp4"
    download_success = download_file_by_name(client, box_folder_id, file_name_to_download, folder_video_path)

    if download_success:
        print("Tải video thành công!")
    else:
        print("Không thể tải video.")
    delete_file_by_name(client, box_folder_id, file_name_to_download)
    delete(file_path)
    file_path_up_to_discord = f"/home/thanhnam/Desktop/Tiktok/videos/videos/{file_name_to_download}"
    print(file_path_up_to_discord)
    response_text = send_message_with_file(webhook_url, file_path_up_to_discord, tiktok_url, tiktok_description)
    print(response_text)
    delete_file_in_folder(file_path_up_to_discord)
if __name__ == "__main__":
    main()
