import asyncio
import json
import os
import re
import time
from setup_logger import logger
from config_reader import proxy_config
from spawnbot import bot


async def download_video_from_youtube(url, user_id):
    proxy = proxy_config()['http']
    command_info = ['yt-dlp', '-j', url]

    info_message = await bot.send_message(chat_id=user_id, text="Загрузка: 0% | Размер: 0 | Скорость: 0")
    info_message_id = info_message.message_id

    if proxy:
        command_info.insert(1, '--proxy')
        command_info.insert(2, proxy)

    process_info = await asyncio.create_subprocess_exec(
        *command_info,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process_info.communicate()

    if process_info.returncode != 0:
        error_message = f"Error occurred: {stderr.decode()}"
        logger.error(error_message)
        return None

    try:
        video_info = json.loads(stdout.decode())
    except json.JSONDecodeError as e:
        error_message = f"JSON decoding failed: {e}"
        logger.error(error_message)
        return None

    video_title = video_info['title']

    command_download = [
        'yt-dlp',
        '-f', 'bestvideo+bestaudio',
        '--merge-output-format', 'mp4',
        '--newline',
        '-o', f"video/{video_title}.%(ext)s",
        url
    ]

    if proxy:
        command_download.insert(1, '--proxy')
        command_download.insert(2, proxy)

    process = await asyncio.create_subprocess_exec(
        *command_download,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    last_progress = None
    last_time = time.time()

    while True:
        output = await process.stdout.readline()
        if process.returncode is not None and output == b'':
            break

        if output:
            output = output.decode()  # Декодирование байтов в строку
            match = re.search(
                r'\[download\]\s+(\d+\.\d+)%\s+of\s+~?\s*(\d+\.\d+\w+)\s+at\s+(\d+\.\d+\w+/s)', output)
            if match:
                progress = float(match.group(1))
                downloaded_size = match.group(2)
                download_speed = match.group(3)

                current_time = time.time()

                if last_progress is None or (current_time - last_time >= 2):
                    await bot.send_chat_action(user_id, 'upload_video')
                    await bot.edit_message_text(chat_id=user_id,
                                          message_id=info_message_id,
                                          text=f"Загрузка: {progress}% | Размер: {downloaded_size} | Скорость: {download_speed}")
                    last_progress = progress
                    last_time = current_time

    await process.wait()
    logger.info(f"Video downloaded successfully: {video_title}")
    await bot.edit_message_text(chat_id=user_id,
                          message_id=info_message_id,
                          text="Загрузка: 100%  ✅")
    #for file in os.listdir('edit_content'):
    #    if video_title in file:
    #        video_title = file
    #        break
    return f'video/{video_title}.mp4'
