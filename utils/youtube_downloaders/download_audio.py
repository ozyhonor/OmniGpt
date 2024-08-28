import asyncio
import re
import os
from setup_logger import logger
from config_reader import proxy_config


async def download_audio_from_youtube(url):
    proxy = proxy_config()['http']
    command_audio = [
        'yt-dlp',
        '-f', 'bestaudio',  # Загрузка аудио в лучшем качестве
        '--extract-audio',  # Извлечение аудио
        '--audio-format', 'mp3',  # Конвертация в формат mp3
        '-o', f"audio_files/%(title)s.%(ext)s",
        url
    ]

    if proxy:
        command_audio.insert(1, '--proxy')
        command_audio.insert(2, proxy)

    process = await asyncio.create_subprocess_exec(
        *command_audio,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    output = stdout.decode()
    errors = stderr.decode()

    logger.debug(f"yt-dlp stdout: {output}")
    logger.debug(f"yt-dlp stderr: {errors}")

    if process.returncode != 0:
        error_message = f"Error occurred: {errors}"
        logger.error(error_message)
        return None

    # Обновленное регулярное выражение для поиска пути к файлу .mp3, включая сообщение "has already been downloaded"
    match = re.search(r'audio_files\/(.+\.mp3)', output)
    if match:
        audio_title = match.group(0)  # Полный путь к аудиофайлу
        logger.info(f"Audio downloaded successfully: {audio_title}")
        return audio_title
    else:
        logger.error("Failed to find audio file in yt-dlp output.")
        return None
