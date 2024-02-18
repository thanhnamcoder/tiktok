from flask import Flask

# Tạo một ứng dụng Flask
app = Flask(__name__)

# Định nghĩa route cho trang chủ
@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    # Chạy ứng dụng trên cổng 5000
    app.run()
