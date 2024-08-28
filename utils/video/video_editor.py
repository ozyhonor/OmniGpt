from db.database import db
import asyncio
from setup_logger import logger
import os
from utils.video.local_requests.get_subtitles import send_recognize_request
from utils.video.support_scripts.convert_json_to_srt import json_to_srt
from utils.video.support_scripts.convert_srt_to_ass import srt_to_ass
from utils.video.support_scripts.get_subtitles_content import get_subtitles_content
from utils.speech_requests import openai_audio_request
from utils.video.create_translate import create_translate_text
from utils.video.local_requests.get_translated_subtitles import translate_subtitles
import re
from spawnbot import bot
import time
import math


async def replace_audio(video_path, audio_path):
    output_video = video_path.replace('.mp4', '_translated_chunk.mp4')
    command = [
        'ffmpeg',
        '-i', audio_path,  # Новая аудиодорожка
        '-i', video_path,  # Оригинальное видео
        '-shortest',       # Обрезка видео до длины аудиодорожки
        output_video        # Путь для сохранения нового видеофайла
    ]

    logger.info(f"Running command: {' '.join(command)}")

    # Запуск команды ffmpeg в асинхронном режиме
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Ожидание завершения процесса и получение вывода
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        logger.info(f"Video created successfully: {output_video}")
        logger.debug(f"ffmpeg stdout: {stdout.decode()}")
    else:
        logger.error(f"Error occurred while processing video: {stderr.decode()}")
        logger.debug(f"ffmpeg stderr: {stderr.decode()}")


async def add_subtitles_to_video(input_video: str, input_subtitles: str, user_id: int):
    output_video = input_video.replace('.mp4', '_with_subs.mp4')
    info_message = await bot.send_message(user_id, 'Cубтитры: 0')
    info_message_text = info_message.text
    info_message_id = info_message.message_id
    command = [
        'ffmpeg',
        '-y',
        '-i', input_video,
        '-vf', f'subtitles={input_subtitles}',
        '-progress', 'pipe:1',
        output_video
    ]

    logger.info(f"Running command: {' '.join(command)}")

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    last_time = time.time()

    while True:
        output = await process.stdout.readline()
        if process.returncode is not None and output == b'':
            break

        if output:
            output = output.decode().strip()
            frame_match = re.search(r'frame=\s*(\d+)', output)

            frame = frame_match.group(1) if frame_match else 'N/A'
            current_time = time.time()

            if current_time - last_time >= 2 and info_message_text != f'Cубтитры: {frame}':

                await bot.edit_message_text(chat_id=user_id, message_id=info_message_id, text=f'Cубтитры: {frame}')
                last_time = current_time


    await process.wait()

    if process.returncode == 0:
        logger.info("Video successfully processed!")
        await bot.edit_message_text(chat_id=user_id, message_id=info_message_id, text=f'Cубтитры: 100% ✅')
    else:
        logger.error(f"Process ended with return code {process.returncode}. Please check the output above for errors.")

    return output_video


async def get_video_duration(input_video: str) -> float:

    command = ['ffmpeg', '-i', input_video]

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        output = stderr.decode()

        logger.info(f'ffmpeg output: {output}')

        duration_match = re.search(r"Duration: (\d+):(\d+):(\d+.\d+)", output)
        if duration_match:
            hours = int(duration_match.group(1))
            minutes = int(duration_match.group(2))
            seconds = float(duration_match.group(3))
            duration = hours * 3600 + minutes * 60 + seconds
            logger.info(f'Duration of video {input_video}: {duration} seconds')
            return duration
        else:
            logger.error('Could not find duration in ffmpeg output.')

    except Exception as e:
        logger.error(f'Unexpected error occurred: {e}')


async def create_translated_chunks(video_path, subtitles_path, user_id):
    voice = await db.get_user_setting('synthes_voice', user_id)
    output_file = ...
    speed = await db.get_user_setting('synthes_speed', user_id)
    model = 'tts-1'

    subtitles = await get_subtitles_content(subtitles_path)
    video_chunks = []
    for chunk in subtitles:
        start, end, text = chunk.start, chunk.end, chunk.content
        translated_text = await create_translate_text(text)
        video_fragment = await trim_by_timecode(video_path, start, end)
        base_name, ext = os.path.splitext(video_fragment)
        audio_path = f"{base_name}_translated.mp3"
        translated_audio_fragment = await openai_audio_request(voice, translated_text, audio_path, speed, model)
        translated_audio_fragment_path = translated_audio_fragment[1]
        changed_audio_video_fragment = await replace_audio(video_fragment, translated_audio_fragment_path)
        video_chunks.append(changed_audio_video_fragment)

    return video_chunks


async def trim_by_timecode(video_path, start, end):

    base_name = os.path.basename(video_path)
    name, ext = os.path.splitext(base_name)

    output_file = f"{name}_{start}_{end}{ext}"

    output_path = os.path.join(os.path.dirname(video_path), output_file)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", f"{video_path}",
        "-ss", f"{start}",
        "-to", f"{end}",
        output_path
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        logger.info(f"Команда выполнена успешно, файл сохранен как {output_path}")
        return output_path
    else:
        logger.error(f"Ошибка выполнения команды: {stderr.decode()}")


async def extract_audio(input_video: str):

    base_name = os.path.splitext(input_video)[0]
    output_audio = f'{base_name}.mp3'

    command = ['ffmpeg', '-y', '-i', input_video, output_audio]

    logger.info(f'Starting audio extraction from {input_video} to {output_audio}')

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            logger.info(f'Successfully extracted audio to {output_audio}')
            return output_audio
        else:
            logger.error(f'Error in extracting audio: {stderr.decode()}')

    except Exception as e:
        logger.error(f'Unexpected error occurred: {e}')


async def calculate_length(number_video_part, video_duraction):
    return {'start': number_video_part*600, 'end': min(600*(number_video_part+1), video_duraction)}


async def process_video(video_path, user_id):
    timestamps:str = await db.get_user_setting('timestamps', user_id)
    subtitles:bool = await db.get_user_setting('subtitles', user_id)
    translator:bool = await db.get_user_setting('translator', user_id)
    auto_subtitles:bool = await db.get_user_setting('smart_sub', user_id)
    words_per_chunk:int = await db.get_user_setting('max_words', user_id)
    overlap:int = await db.get_user_setting('overlap', user_id)
    max_duration_seconds = 600 # time to send to recognize

    videos_path_by_timecode = []
    for part in timestamps.split(' '):
        if part != '0':
            start, end = part[0], part[1]
            trimmed_video_path = await trim_by_timecode(video_path, start, end)
            videos_path_by_timecode.append(trimmed_video_path)

    if len(videos_path_by_timecode) == 0: videos_path_by_timecode.append(video_path)
    for video in videos_path_by_timecode:
        if subtitles or translator:
            video_duration = await get_video_duration(video)
            num_pieces = math.ceil(video_duration / max_duration_seconds)
            video_path_by_ten_minutes = []
            for number_video_part in range(num_pieces):
                ten_minutes_timecode = await calculate_length(number_video_part, video_duration)
                start, end = ten_minutes_timecode['start'], ten_minutes_timecode['end']

                if video_duration > end:
                    ten_minute_video = await trim_by_timecode(video, start, end) # ?
                    video_path_by_ten_minutes.append(ten_minute_video)
                else: video_path_by_ten_minutes.append(video)

                video_to_process = video_path_by_ten_minutes[number_video_part]

                audio_path = await extract_audio(video_to_process)
                subtitle_path = await send_recognize_request(audio_path, auto_subtitles)
                if not auto_subtitles: subtitle_path = json_to_srt(subtitle_path, words_per_chunk, overlap)

                if subtitles:
                    if translator: translated_subtitles_path = await translate_subtitles(subtitle_path)
                    else: translated_subtitles_path = None
                    subtitle_path_to_add_sub = await srt_to_ass(translated_subtitles_path or subtitle_path, user_id)
                    video_with_subtitles = await add_subtitles_to_video(video_to_process, subtitle_path_to_add_sub, user_id)
                    print(video_with_subtitles)

                if translator:
                    translated_subtitles = ...
                    translated_chunks = await create_translated_chunks(video_to_process, subtitle_path, user_id)
                    print(translated_chunks)
                    original_chunks = ...

