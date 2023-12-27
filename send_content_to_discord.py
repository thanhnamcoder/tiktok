import discord
from discord.ext import tasks
import asyncio
from Oauth2 import *
import re
import json
from discord.ext import commands


with open('config.json', 'r') as config_file:
    config = json.load(config_file)

input_folder_name = "hanhhtrann99"
file_descreption_to_download = f"{input_folder_name}_description.txt"
folder_description_path = f"videos/description"
file_path = f"videos/description/{input_folder_name}_description.txt"
box_folder_id = "0"
folder_video_path = "videos/videos"
webhook_url = 'https://discordapp.com/api/webhooks/1185876707043983493/kEyLEsJPHzyEyplAk3Z9ikEfqRO5N2HwaPE0fiBNqiWArwpNlk81LwGYbno22lF3dYVx'

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Cho phép đọc và nhận tin nhắn
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or('^'), intents=intents)

stop_loop = False  # Biến để kiểm soát việc dừng loop
loop_is_running = False  # Biến để kiểm tra xem loop có đang chạy không
date_time = current_time_with_format()

@bot.event
async def on_message(message):
    global stop_loop, loop_is_running, send_loop_message

    # Kiểm tra xem tin nhắn được gửi có phải từ bot không
    if message.author == bot.user:
        return

    if message.content == 'Start':
        await message.channel.send(f'{date_time}')
        stop_loop = False
        if not loop_is_running:
            send_loop_message.start()  # Khởi động loop nếu nó đã dừng
            loop_is_running = True
            print("Start Success")

        # Xóa tin nhắn người dùng sau khi nhập lệnh "Start"
        await message.delete()


            
            



        
        

remaining = 5
@tasks.loop(seconds=remaining)
async def send_loop_message():
    global loop_is_running

    if stop_loop:
        send_loop_message.stop()  # Nếu stop_loop là True, dừng loop
        return


    oauth = oauth2_process()
    client = Client(oauth)
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
    file_path_up_to_discord = f"videos/videos/{file_name_to_download}"
    
    send_message(webhook_url, file_path_up_to_discord, tiktok_description)
    response_text = send_message_with_file(webhook_url, file_path_up_to_discord, tiktok_url)
    delete_file_in_folder(file_path_up_to_discord)
    print("Gửi tin nhắn thành công")

    for remaining_seconds in range(remaining, 0, -1):
        print(f"Đang chạy lại sau {remaining_seconds} giây...")
        await asyncio.sleep(1)

    # Tắt vòng lặp khi hoàn thành gửi tin nhắn thành công
    send_loop_message.stop()
    print("Loop stopped after sending message successfully")

        

    
@bot.event
async def on_ready():
    oauth = oauth2_process()
    client = Client(oauth)
    
    print("Bot is ready!")
    download_file_by_name(client, box_folder_id, file_descreption_to_download, folder_description_path)
    delete_file_by_name(client, box_folder_id, file_descreption_to_download)
    send_loop_message.start()
        # Gửi tin nhắn khi hoàn thành khởi chạy hàm send_loop_message
    channel = bot.get_channel(1185824039218974763)  # Thay YOUR_CHANNEL_ID bằng ID của kênh muốn gửi tin nhắn
    await channel.send("===============DONE===============")
    

# Thay YOUR_BOT_TOKEN bằng token của bot Discord của bạn
token_discord = config.get('discord_token')
bot.run(token_discord)

