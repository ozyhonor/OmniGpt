import asyncio
import json
import os
import re
import time
from setup_logger import logger
from config_reader import yt_mail_for_downloading, yt_pass_for_downloading, po
from config_reader import proxy_config
from spawnbot import bot


async def download_video_from_youtube(url, user_id):
    proxy = proxy_config()['http']

    command_info = [
        'yt-dlp',
        "--extractor-args",
        f"youtube:player-client=web,default;po_token=web+{po}",
        "--cookies",
        "cookies.txt",
        '-j',
        url
    ]
    info_message = await bot.send_message(chat_id=user_id, text="Начинаем загрузку видео...")
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
        error_message = f"Произошла ошибка при получении информации о видео: {stderr.decode()}"
        logger.error(error_message)
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=info_message_id,
                                    text="Ошибка при получении информации о видео ❌")
        return None

    try:
        video_info = json.loads(stdout.decode())
    except json.JSONDecodeError as e:
        error_message = f"Ошибка при декодировании JSON: {e}"
        logger.error(error_message)
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=info_message_id,
                                    text="Ошибка при декодировании данных видео ❌")
        return None

    video_title = video_info['title']

    command_download = [
        'yt-dlp',
        "--cookies",
        "./cookies.txt",
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

    # Ждем завершения процесса загрузки
    await process.wait()

    if process.returncode == 0:
        logger.info(f"Видео успешно загружено: {video_title}")
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=info_message_id,
                                    text="Видео успешно загружено ✅")
        return f'video/{video_title}.mp4'
    else:
        error_message = f"Ошибка при загрузке видео: {stderr.decode()}"
        logger.error(error_message)
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=info_message_id,
                                    text="Ошибка при загрузке видео ❌")
        return None
