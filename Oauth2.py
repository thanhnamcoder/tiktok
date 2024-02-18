from boxsdk import Client, OAuth2
import os
import requests
from database import get_token

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
    box_client_secret = get_token("box")

    load_tokens_from_file()

    # Nếu đã có tokens, sử dụng chúng
    if saved_access_token and saved_refresh_token:
        oauth = OAuth2(
            client_id='lj0iuv31t35gm3id4rsvewaa7wfy83sd',
            client_secret=box_client_secret,
            access_token=saved_access_token,
            refresh_token=saved_refresh_token,
            store_tokens=store_tokens_to_file,
        )
    else:
        # Nếu không có tokens, yêu cầu xác thực từ người dùng
        oauth = OAuth2(
            client_id='lj0iuv31t35gm3id4rsvewaa7wfy83sd',
            client_secret=box_client_secret,
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

def delete_messages_in_channel():
    channel_id = "1186950282849042513"
    bot_token = get_token("discord")
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {bot_token}"
    }

    # Lấy danh sách tin nhắn trong kênh
    response = requests.get(url, headers=headers)
    messages = response.json()

    # Xóa từng tin nhắn trong kênh
    for message in messages:
        message_id = message['id']
        delete_url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}"
        delete_response = requests.delete(delete_url, headers=headers)
        if delete_response.status_code == 204:
            print(f"Đã xóa tin nhắn có ID {message_id}")
        else:
            print(f"Không thể xóa tin nhắn có ID {message_id}. Mã lỗi:", delete_response.status_code)



