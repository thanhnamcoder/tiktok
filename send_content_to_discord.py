import discord
from discord.ext import tasks
import asyncio
from Oauth2 import *
import re
import json
from discord.ext import commands
import time


with open('config.json', 'r') as config_file:
    config = json.load(config_file)

input_folder_name = "ntkh.03"
file_descreption_to_download = f"{input_folder_name}_description.txt"
folder_description_path = f"videos/description"
file_path = f"videos/description/{input_folder_name}_description.txt"
box_folder_id = "0"
folder_video_path = "videos/videos"
webhook_url = 'https://discordapp.com/api/webhooks/1186950849537249361/jEFMfjsioLRm8cIVLBnCuJcPJWepjlXWsqwPCGy131wWq2nQ-6GsO_WR6zcysL2ghvtr'

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Cho phép đọc và nhận tin nhắn
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or('^'), intents=intents)

stop_loop = False  # Biến để kiểm soát việc dừng loop
loop_is_running = False  # Biến để kiểm tra xem loop có đang chạy không
remine_time = 60


@bot.event
async def on_message(message):
    global stop_loop, loop_is_running, send_loop_message

    if message.author == bot.user:
        return

    if message.content == 'Start':

        # Khóa phòng chat
        overwrites = {
            message.guild.default_role: discord.PermissionOverwrite(send_messages=False),
            message.author: discord.PermissionOverwrite(send_messages=False),
            bot.user: discord.PermissionOverwrite(send_messages=True)
        }
        await message.channel.edit(overwrites=overwrites)

        stop_loop = False
        if not loop_is_running:
            loop_is_running = True
            print("Start Success")
            await message.channel.send("Đang chuẩn bị content!")

            # Gửi tin nhắn bắt đầu loop và chờ send_loop_message.start() hoàn thành
            
            # Chờ send_loop_message.start() hoàn thành
            send_loop_message.start()
            await asyncio.sleep(2)  # Chờ 2 giây

            # Gửi tin nhắn thông báo sau khi start loop
            notification_msg = await message.channel.send(f"Deleting messages in {remine_time} seconds...")

            # Đếm ngược từ 10 xuống 0 và gửi tin nhắn cập nhật
            for i in range(remine_time, -1, -1):
                try:
                    await notification_msg.edit(content=f"Deleting messages in {i} seconds...")
                    await asyncio.sleep(1)
                except discord.NotFound:
                    pass

            # Xóa tin nhắn thông báo cuối cùng
            try:
                await notification_msg.delete()
            except discord.NotFound:
                pass

            # Xóa tin nhắn trong kênh
            async for msg in message.channel.history(limit=None):
                try:
                    retrieved_msg = await message.channel.fetch_message(msg.id)
                    await retrieved_msg.delete()
                except discord.NotFound:
                    pass

            loop_is_running = False


        

remaining = 0
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
    

# Thay YOUR_BOT_TOKEN bằng token của bot Discord của bạn
token_discord = config.get('discord_token')
bot.run(token_discord)

