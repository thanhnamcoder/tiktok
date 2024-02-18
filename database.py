import mysql.connector

def connect_to_mysql():
    try:
        # Thay đổi các thông tin kết nối dựa trên cấu hình của bạn
        connection = mysql.connector.connect(
            host="103.97.126.22",
            user="axnflrzj_thanhnam",
            password="Nguyen2004nam",
            database="axnflrzj_data_tiktok"
        )
        if connection.is_connected():
            print("Kết nối đến MySQL thành công.")
            return connection
    except mysql.connector.Error as error:
        print(f"Lỗi khi kết nối đến MySQL: {error}")
        return None


def get_token(token_type):
    connection = connect_to_mysql()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            # Thực hiện truy vấn dựa trên loại token
            if token_type == "discord":
                query = "SELECT discord_token FROM tokens LIMIT 1"
            elif token_type == "box":
                query = "SELECT box_client_secret FROM tokens LIMIT 1"
            else:
                print("Loại token không hợp lệ.")
                return None

            cursor.execute(query)
            token_data = cursor.fetchone()

            if token_data:
                # Trả về giá trị của cột tương ứng với loại token
                if token_type == "discord":
                    return token_data["discord_token"]
                elif token_type == "box":
                    return token_data["box_client_secret"]
            else:
                print("Không tìm thấy dữ liệu token trong cơ sở dữ liệu.")
                return None
        except mysql.connector.Error as error:
            print(f"Lỗi khi truy vấn dữ liệu: {error}")
            return None
        finally:
            cursor.close()
            connection.close()
    else:
        return None

def delete_single_record_from_mysql():
    try:
        # Kết nối đến MySQL
        connection = connect_to_mysql()

        if connection.is_connected():
            cursor = connection.cursor()

            # Câu lệnh SQL để xóa một bản ghi đầu tiên từ bảng
            delete_query = "DELETE FROM TikTokData LIMIT 1"

            # Thực thi câu lệnh SQL
            cursor.execute(delete_query)

            # Lưu các thay đổi vào cơ sở dữ liệu
            connection.commit()

            print("Đã xóa một bản ghi từ bảng thành công.")
    except mysql.connector.Error as error:
        print(f"Lỗi khi thực hiện câu lệnh SQL: {error}")
    finally:
        # Đóng kết nối
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_single_tiktok_info_from_mysql():
    url = ''
    description = ''

    try:
        connection = connect_to_mysql()
        if connection:
            cursor = connection.cursor()

            cursor.execute("SELECT url, description FROM TikTokData LIMIT 1")
            record = cursor.fetchone()

            if record:
                url = record[0]
                description = record[1]
            else:
                print("Không tìm thấy dữ liệu trong bảng.")
            
            cursor.close()
            connection.close()
        else:
            print("Không thể kết nối đến MySQL.")

    except Exception as e:
        print(f"An error occurred while querying MySQL: {str(e)}")
    
    return url, description