import asyncio
import json
import os
import re
from setup_logger import logger
from spawnbot import bot
from config_reader import proxy_config


async def download_subtitles_from_youtube(url, user_id, language):
    proxy = proxy_config().get('http')
    command_subtitles = [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--cookies",
        "cookies.txt",
        "--write-auto-subs",
        "--sub-lang", language,
        "--sub-format", "ttml",
        "--convert-subs", "srt",
        "--output", f"subtitles/%(title)s.%(ext)s",
        url
    ]


    if proxy:
        command_subtitles.insert(1, '--proxy')
        command_subtitles.insert(2, proxy)

    process_subtitles = await asyncio.create_subprocess_exec(
        *command_subtitles,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process_subtitles.communicate()

    output = stdout.decode()
    errors = stderr.decode()


    if process_subtitles.returncode != 0:
        logger.error(f"Error occurred: {errors}")
        await bot.send_message(user_id, 'Субтитры недоступны')
        return "Subtitles not available or download failed."

    # Обновленное регулярное выражение для поиска файла .srt после конвертации
    match = re.search(r'\[SubtitlesConvertor\] Converting subtitles\nDeleting original file .+\n', output)
    if match:
        # Теперь нужно найти итоговый .srt файл
        for file in os.listdir('subtitles'):
            if file.endswith('.srt'):
                subtitle_file = file
                logger.info(f"Subtitles downloaded successfully: {subtitle_file}")

                output_file = subtitle_file.replace('.srt', 'e.txt')
                with open('subtitles/'+output_file, 'w', encoding='utf-8') as outfile:
                    with open('subtitles/'+subtitle_file, 'r', encoding='utf-8') as infile:
                        for line in infile:
                            # Удаляем строки с таймкодами и номера субтитров
                            if re.match(r'^\d+$', line) or re.match(r'^\d{2}:\d{2}:\d{2},\d{3} -->', line):
                                continue
                            # Удаляем HTML-теги
                            clean_line = re.sub(r'<[^>]*>', '', line).strip()
                            if clean_line:  # Записываем только не пустые строки
                                outfile.write(clean_line + '\n')

                return f'subtitles/{output_file}'
    else:
        logger.error("Failed to find subtitles in yt-dlp output.")
        await bot.send_message(user_id, 'Субтитры недоступны')
        return "Subtitles not available or download failed."