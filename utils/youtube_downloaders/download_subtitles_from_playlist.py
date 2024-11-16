import asyncio
import json
import os
import re
from aiogram.types import Message
from setup_logger import logger
from spawnbot import bot
from config_reader import proxy_config


def clean_subtitles(input_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    cleaned_lines = []
    prev_line = None

    for line in lines:
        # Убираем лишние пробелы и знаки переноса строки
        line = line.strip()

        # Пропускаем пустые строки
        if not line:
            continue

        # Если строка не повторяется подряд, добавляем её в список
        if line != prev_line:
            cleaned_lines.append(line)
        prev_line = line

    # Сохраняем очищенные субтитры в новый файл
    output_file = input_file.replace('.txt', '_cleaned.txt')
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("\n".join(cleaned_lines))

    print(f"Cleaned subtitles saved to {output_file}")
    return output_file


async def download_subtitles_from_video(video_url, language, number, proxy=None):
    # Получаем список файлов до загрузки
    subtitles_dir = 'subtitles'



    base_command = [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--cookies",
        "cookies.txt",
        "--write-auto-subs",
        "--sub-lang", language,
        "--sub-format", "ttml",
        "--convert-subs", "srt",
        "--output", f"{subtitles_dir}/sub{number}",
        video_url
    ]
    output = f"{subtitles_dir}/sub{number}.{language}.srt"
    if proxy:
        base_command.insert(1, '--proxy')
        base_command.insert(2, proxy)

    process_subtitles = await asyncio.create_subprocess_exec(
        *base_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process_subtitles.communicate()
    errors = stderr.decode()

    if process_subtitles.returncode != 0 or 'ERROR' in errors:
        logger.warning(f"Skipped video {video_url}: {errors}")
        return None

    # Проверяем новые файлы в папке после загрузки

    subtitle_file = output
    logger.info(f"Subtitles downloaded successfully: {subtitle_file}")
    return subtitle_file



async def download_subtitles_from_playlist(playlist_url, user_id, language='ru', message:Message = None):
    proxy = proxy_config().get('http')
    user_id = message.from_user.id
    command_list_videos = [
        'yt-dlp',
        "--cookies",
        "cookies.txt",
        '--flat-playlist', '--dump-json', playlist_url
    ]
    if proxy:
        command_list_videos.insert(1, '--proxy')
        command_list_videos.insert(2, proxy)

    process_list_videos = await asyncio.create_subprocess_exec(
        *command_list_videos,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process_list_videos.communicate()

    if process_list_videos.returncode != 0:
        logger.error(f"Error occurred while listing videos: {stderr.decode()}")
        await bot.send_message(user_id, 'Ошибка при получении списка видео в плейлисте')
        return "Failed to retrieve playlist."

    video_urls = [f"https://www.youtube.com/watch?v={json.loads(line)['id']}" for line in stdout.decode().splitlines()]
    info_message = await message.answer(f'Процесс работы 0/{len(video_urls)}')
    # Размер блока
    chunk_size = 33
    subtitles_files = []

    # Обработка плейлиста частями
    for i in range(0, len(video_urls), chunk_size):
        chunk = video_urls[i:i + chunk_size]
        tasks = [download_subtitles_from_video(url, language, x + i, proxy) for x, url in enumerate(chunk)]
        chunk_results = await asyncio.gather(*tasks)
        subtitles_files.extend([file for file in chunk_results if file is not None])
        try:
            await info_message.edit_text(f'Процесс работы {len(subtitles_files)}/{len(video_urls)}')
        except:
            ...

    if not subtitles_files:
        await bot.send_message(user_id, f'Субтитры на языке "{language}" недоступны для всех видео в плейлисте')
        return "Subtitles not available or download failed."

    try:
        await info_message.edit_text(f'Процесс работы {len(subtitles_files)}/{len(video_urls)}')
    except:
        ...

    # Объединяем текст из всех файлов субтитров
    output_file = 'subtitles/combined_subtitles.txt'
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for input_file in subtitles_files:
            try:
                with open(input_file, 'r', encoding='utf-8') as infile:
                    for line in infile:
                        # Удаляем строки с таймкодами и номера субтитров
                        if re.match(r'^\d+$', line) or re.match(r'^\d{2}:\d{2}:\d{2},\d{3} -->', line):
                            continue
                        # Удаляем HTML-теги
                        clean_line = re.sub(r'<[^>]*>', '', line).strip()
                        if clean_line:  # Записываем только не пустые строки
                            outfile.write(clean_line + '\n')
            except:
                logger.error('No file '+ input_file)

    return output_file
