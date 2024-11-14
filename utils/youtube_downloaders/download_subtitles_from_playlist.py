import asyncio
import json
import os
import re
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


async def download_subtitles_from_video(video_url, language, proxy=None):
    # Получаем список файлов до загрузки
    subtitles_dir = 'subtitles'
    existing_files = set(os.listdir(subtitles_dir))

    # Команда для загрузки субтитров
    base_command = [
        'yt-dlp',
        "--cookies",
        "cookies.txt",
        '--write-sub',
        '--write-auto-subs',
        '--convert-subs', 'srt',
        '--sub-lang', language,
        '--skip-download',
        '-o', f"{subtitles_dir}/%(title)s.%(ext)s",
        video_url
    ]

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
    new_files = set(os.listdir(subtitles_dir)) - existing_files
    srt_files = [file for file in new_files if file.endswith('.srt')]

    if srt_files:
        # Берём первый найденный файл .srt (должен быть только один)
        subtitle_file = os.path.join(subtitles_dir, srt_files[0])
        logger.info(f"Subtitles downloaded successfully: {subtitle_file}")
        return subtitle_file
    else:
        logger.warning(f"No subtitle file found for video {video_url}")
        return None

async def download_subtitles_from_playlist(playlist_url, user_id, language='ru'):
    proxy = proxy_config().get('http')

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

    tasks = [download_subtitles_from_video(url, language, proxy) for url in video_urls]
    subtitles_files = await asyncio.gather(*tasks)

    subtitles_files = [file for file in subtitles_files if file is not None]

    if not subtitles_files:
        await bot.send_message(user_id, f'Субтитры на языке "{language}" недоступны для всех видео в плейлисте')
        return "Subtitles not available or download failed."

    # Объединяем текст из всех файлов субтитров
    combined_text = ""
    for srt_file in subtitles_files:
        with open(srt_file, 'r', encoding='utf-8') as file:
            for line in file:
                # Удаляем строки с таймкодами и номера субтитров
                if not re.match(r'^\d+$', line) and not re.match(
                        r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line):
                    combined_text += line.strip() + "\n"

    # Сохраняем объединённый текст в новый .txt файл
    output_file = 'subtitles/combined_subtitles.txt'
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(combined_text)

    output_file = clean_subtitles(output_file)
    return output_file