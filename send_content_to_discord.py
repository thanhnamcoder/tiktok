import discord
from discord.ext import tasks
import asyncio
from Oauth2 import *
import re
import json

with open('config.json', 'r') as config_file:
    config = json.load(config_file)


input_folder_name = "hanhhtrann99"
file_path = f"videos/description/{input_folder_name}_description.txt"
box_folder_id = "0"
folder_video_path = "videos/videos"
webhook_url = 'https://discordapp.com/api/webhooks/1186950849537249361/jEFMfjsioLRm8cIVLBnCuJcPJWepjlXWsqwPCGy131wWq2nQ-6GsO_WR6zcysL2ghvtr'


intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.reference: 
        original_msg_id = message.reference.message_id
        original_msg = await message.channel.fetch_message(original_msg_id)
        await original_msg.delete()
        await message.delete()  # This deletes the replied message
        # await message.channel.send(f"ID tin nhắn gốc bạn đã reply là: {original_msg_id}") 
        
        

remaining = 3600
@tasks.loop(seconds=remaining)
async def send_loop_message():
        date_time = current_time_with_format()
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
        # print(file_path_up_to_discord)
        send_message(webhook_url, file_path_up_to_discord, tiktok_description)
        response_text = send_message_with_file(webhook_url, file_path_up_to_discord, tiktok_url, date_time)
        # print(response_text)
        delete_file_in_folder(file_path_up_to_discord)
        print("Gửi tin nhắn thành công")
        for remaining_seconds in range(remaining, 0, -1):
            print(f"Đang chạy lại sau {remaining_seconds} giây...")
            await asyncio.sleep(1)
    

    
@client.event
async def on_ready():
    print('Bot đã kết nối thành công!')
    oauth = oauth2_process()
    client = Client(oauth)

    folder_description_path = f"videos/description"
    box_folder_id = "0"
    file_descreption_to_download = f"{input_folder_name}_description.txt"
    folder_video_path = "videos/videos"

    download_file_by_name(client, box_folder_id, file_descreption_to_download, folder_description_path)
    # delete_file_by_name(client, box_folder_id, file_descreption_to_download)


    date_time = current_time_with_format()
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
    # print(file_path_up_to_discord)
    send_message(webhook_url, file_path_up_to_discord, tiktok_description)
    response_text = send_message_with_file(webhook_url, file_path_up_to_discord, tiktok_url, date_time)
    # print(response_text)
    delete_file_in_folder(file_path_up_to_discord)
    print("Gửi tin nhắn thành công")
    # print('Bot đã kết nối thành công!')
    # Start the loop here when the bot is ready
    send_loop_message.start()

# Thay YOUR_BOT_TOKEN bằng token của bot Discord của bạn
token_discord = config.get('discord_token')
client.run(token_discord)

