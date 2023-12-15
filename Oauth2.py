from boxsdk import Client, OAuth2
import os

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
            client_secret='Sl5CXKhRrDtzHYPliOyeFBpcTEndP3Ex',
            access_token=saved_access_token,
            refresh_token=saved_refresh_token,
            store_tokens=store_tokens_to_file,
        )
    else:
        # Nếu không có tokens, yêu cầu xác thực từ người dùng
        oauth = OAuth2(
            client_id='lj0iuv31t35gm3id4rsvewaa7wfy83sd',
            client_secret='Sl5CXKhRrDtzHYPliOyeFBpcTEndP3Ex',
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
