from db.database import db
import asyncio
import aiofiles
import srt
from setup_logger import logger
import os
from utils.edit_content.local_requests.yandex_translate import translate_subtitles
from utils.edit_content.local_requests.get_subtitles import send_recognize_request
from utils.edit_content.support_scripts.convert_json_to_srt import json_to_srt
from utils.edit_content.support_scripts.convert_srt_to_ass import srt_to_ass
from utils.edit_content.support_scripts.get_subtitles_content import get_subtitles_content
from utils.speech_requests import openai_audio_request
import re
from spawnbot import bot
import time
import math

from proglog import ProgressBarLogger
from moviepy.editor import VideoFileClip, concatenate_videoclips


class MyBarLogger(ProgressBarLogger):
    def __init__(self):
        super().__init__()
        self.current_progress = "Склейка..."

    def callback(self, **changes):
        for parameter, value in changes.items():
            if parameter == "message":
                self.current_progress = value

    def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars[bar]['total']
        if total:
            percentage = (value / total) * 100
            self.current_progress = f"{bar}: {attr} {percentage:.2f}%"
        else:
            self.current_progress = f"{bar}: {attr} 0.00%"


def extract_percentage(progress_str):
    """Извлекает процент из строки прогресса"""
    match = re.search(r"(\d+(\.\d+)?)%", progress_str)
    if match:
        return match.group(1)
    return None


async def monitor_progress(logger_, u_id, m_id):
    """Асинхронная функция для мониторинга прогресса каждые 3 секунды"""
    previous_progress = None
    while True:
        current_progress = logger_.current_progress
        if current_progress != previous_progress:
            percentage = extract_percentage(current_progress)
            if percentage is not None:
                try:
                    await bot.edit_message_text(f"Склейка клипов: {percentage}%", message_id=m_id, chat_id=u_id)
                except Exception as e:
                    logger.error(e)
            previous_progress = current_progress
        await asyncio.sleep(3)


async def process_videos(video_files, logger_, video_with_subtitles):
    # Создание списка клипов
    new_name = video_with_subtitles.replace('.mp4', 'omni.mp4')

    clips = [VideoFileClip(video) for video in video_files]

    # Объединение клипов
    final_clip = concatenate_videoclips(clips, method="compose")

    # Сохранение финального видео с использованием кастомного логгера
    await asyncio.to_thread(
        final_clip.write_videofile,
        new_name,
        codec='libx264',
        audio_codec='aac',
        logger=logger_
    )
    return new_name

async def add_fade_in(input_file, fade_duration=0.3):
    temp_file = input_file.replace('.mp4', 'fade_in_.mp4')
    # Команда ffmpeg для добавления эффекта появления (fade-in) к видео
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-filter_complex",
        f"fade=t=in:st=0:d={fade_duration},format=yuv420p",
        temp_file
    ]

    # Запуск команды ffmpeg в асинхронном режиме
    process = await asyncio.create_subprocess_exec(
        *ffmpeg_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Ожидание завершения процесса и получение вывода
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"Temporary edit_content file created successfully: {temp_file}")

        # Переименование временного файла в старое имя
        try:
            os.replace(temp_file, input_file)
            print(f"Replaced {input_file} with {temp_file}")
        except Exception as e:
            print(f"Error renaming file: {e}")
            return

        # Удаление старого файла (если он всё еще существует)
        # Не нужно удалять старый файл, если он уже переименован
        # Удаление временного файла не требуется, так как он переименован в старое имя
        print(f"Replaced {input_file} with new file successfully")
    else:
        print(f"Error occurred during processing: {stderr.decode()}")



async def replace_audio(video_path, audio_path):
    output_video = video_path.replace('.mp4', 'translated_and_changed_audio.mp4')
    command = [
        'ffmpeg',
        '-y',
        '-i', audio_path,  # Новая аудиодорожка
        '-i', video_path,
        '-map', '0:a',
        '-map', '1:v',
        '-shortest',       # Обрезка видео до длины аудиодорожки
        output_video        # Путь для сохранения нового видеофайла
    ]

    logger.info(f"Running command: {' '.join(map(str, command))}")

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
        logger.error(f"Error occurred while processing edit_content: {stderr.decode()}")
        logger.debug(f"ffmpeg stderr: {stderr.decode()}")
    print(output_video)

    return output_video


async def add_subtitles_to_video(input_video: str, input_subtitles: str, user_id: int):
    output_video = input_video.replace('.mp4', '_ws.mp4')
    info_message = await bot.send_message(user_id, 'Cубтитры: 0')

    info_message_text = info_message.text
    info_message_id = info_message.message_id

    command = [
        'ffmpeg',
        '-y',
        '-i', f'{input_video}',
        '-vf', f"subtitles='{input_subtitles}'",
        '-progress', 'pipe:1',
        f'{output_video}'
    ]

    # Логируем и выводим команду в консоль
    logger.info(f"Running command: {' '.join(command)}")
    print(f"Running command: {' '.join(command)}")

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
            # Логируем и выводим каждый вывод `ffmpeg` в консоль
            logger.info(output)
            print(output)

            frame_match = re.search(r'frame=\s*(\d+)', output)
            frame = frame_match.group(1) if frame_match else 'N/A'
            current_time = time.time()

            if (current_time - last_time >= 4) and (info_message_text != f'Cубтитры: {frame}'):
                try:
                    await bot.edit_message_text(chat_id=user_id, message_id=info_message_id, text=f'Cубтитры: {frame}')
                except:
                    ...
                last_time = current_time

    await process.wait()
    stdout, stderr = await process.communicate()

    # Логируем и выводим завершение процесса
    if process.returncode == 0:
        logger.info("Video successfully processed!")
        print("Video successfully processed!")
        await bot.edit_message_text(chat_id=user_id, message_id=info_message_id, text=f'Cубтитры: 100% ✅')
    else:
        error_message = f"Process ended with return code {process.returncode}. Please check the output above for errors."
        logger.error(error_message)
        print(error_message)
        logger.error(f"Error output: {stderr.decode('utf-8')}")
        print(f"Error output: {stderr.decode('utf-8')}")
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
            logger.info(f'Duration of edit_content {input_video}: {duration} seconds')
            return duration
        else:
            logger.error('Could not find duration in ffmpeg output.')

    except Exception as e:
        logger.error(f'Unexpected error occurred: {e}')

def time_to_float(time_str):
    time_str = str(time_str).replace(",", ".")
    hours, minutes, seconds = time_str.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

async def create_all_chunks(video_path, subtitles_path, user_id):
    voice = await db.get_user_setting('synthes_voice', user_id)
    output_file = ...
    speed = await db.get_user_setting('translation_speed', user_id)
    model = 'tts-1'
    info_message = await bot.send_message(user_id, 'Обработка видео')
    info_message_id = info_message.message_id
    subtitles = await get_subtitles_content(subtitles_path)
    video_chunks = []
    for x,chunk in enumerate(subtitles):
        try:
            await bot.edit_message_text(f'Процесс работы {x}/{len(subtitles)}', chat_id=user_id, message_id=info_message_id)
        except Exception as e:
            logger.error(e)
        start, end, text = chunk.start, chunk.end, chunk.content
        print('start =', start, 'end=', end)
        print(time_to_float(end) - time_to_float(start))
        if (time_to_float(end) - time_to_float(start)) >= 1:
            video_fragment = await trim_by_timecode(video_path, start, end)
            base_name, ext = os.path.splitext(video_fragment)
            audio_path = f"{base_name}_translated.mp3"
            translated_audio_fragment = await openai_audio_request(voice, text, audio_path, speed, model)
            translated_audio_fragment_path = translated_audio_fragment[0]
            print(translated_audio_fragment_path)
            changed_audio_video_fragment = await replace_audio(video_fragment, translated_audio_fragment_path)
            print(changed_audio_video_fragment)
            do_slow_down = await db.get_user_setting('original_speed', user_id)
            if do_slow_down != 1:
                await slow_down_speed(video_fragment, do_slow_down)
            do_fade_in = 1 #await db.get_user_setting('fade_in', user_id)
            if do_fade_in != 0:
                await add_fade_in(changed_audio_video_fragment)
            video_chunks.append(changed_audio_video_fragment)
            video_chunks.append(video_fragment)

    print(video_chunks)
    try:
        await bot.edit_message_text(f'Процесс работы {len(subtitles)}/{len(subtitles)} ✅', chat_id=user_id, message_id=info_message_id)
    except Exception as e:
        logger.error(e)
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


async def process_video(video_path, user_id, message):
    timestamps:str = await db.get_user_setting('timestamps', user_id)
    subtitles:bool = await db.get_user_setting('subtitles', user_id)
    translator:bool = await db.get_user_setting('translator', user_id)
    auto_subtitles:bool = await db.get_user_setting('smart_sub', user_id)
    words_per_chunk:int = await db.get_user_setting('max_words', user_id)
    overlap:int = await db.get_user_setting('overlap', user_id)
    max_duration_seconds = 600 # time to send to recognize

    new_video_path = None

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
                smart_subtitles = await db.get_user_setting('smart_sub', user_id)
                audio_path = await extract_audio(video_to_process)
                subtitle_path = await send_recognize_request(audio_path, auto_subtitles)
                if not smart_subtitles:
                    subtitle_path = await json_to_srt(subtitle_path, overlap)

                if subtitles:
                    subtitle_path_to_add_sub = await srt_to_ass(subtitle_path, user_id)

                    video_with_subtitles = await add_subtitles_to_video(video_to_process, subtitle_path_to_add_sub, user_id)
                    print(video_with_subtitles)



                if translator:
                    translated_subtitles = subtitle_path.replace('.srt', '_translated.srt')
                    subtitle_path_to_add_sub_translated = await srt_to_ass(translated_subtitles, user_id, marginv=30)
                    video_with_subtitles = await add_subtitles_to_video(video_with_subtitles, subtitle_path_to_add_sub_translated,
                                                                        user_id)

                    all_chunks = await create_all_chunks(video_with_subtitles, translated_subtitles, user_id)

                    message_info = await bot.send_message(user_id, 'Склейка клипов')
                    message_info_id = message_info.message_id
                    logger_ = MyBarLogger()
                    monitoring_task = asyncio.create_task(monitor_progress(logger_, user_id, message_info_id))
                    new_video_path = await process_videos(all_chunks, logger_, video_with_subtitles)
                    monitoring_task.cancel()
                    try:
                        await bot.edit_message_text('Склейка 100% ✅', chat_id=user_id, message_id=message_info_id)
                        await monitoring_task
                    except asyncio.CancelledError:
                        pass
    return new_video_path




async def slow_down_speed(name, slow_down):
    # Определяем значение setpts на основе коэффициента замедления
    slow_setpts = {0.5: 2, 0.8: 1.25, 0.625: 1.6}[slow_down]

    # Формируем команду ffmpeg
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", name,
        "-filter_complex", f"[0:v]setpts={slow_setpts}*PTS[v];[0:a]atempo={slow_down}[a]",
        "-map", "[v]",
        "-map", "[a]",
        name.replace('.mp4', 'slowed_.mp4')
    ]

    # Запускаем команду ffmpeg в асинхронном режиме
    process = await asyncio.create_subprocess_exec(
        *ffmpeg_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Ожидаем завершения процесса и получаем вывод
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print(f"Error occurred: {stderr.decode()}")
        return None

    # Обработка файлов после завершения ffmpeg
    file_name2 = name.replace('.mp4', 'slowed_.mp4')

    os.remove(name)
    os.rename(file_name2, name)

    return name


async def replace_srt_lines_async(srt_path, new_text):
    # Новый путь для сохранения файла с суффиксом "_translated_ready"
    output_path = srt_path.replace('.srt', '_translated_ready.srt')

    # Асинхронное чтение оригинального файла субтитров
    async with aiofiles.open(srt_path, 'r', encoding='utf-8') as srt_file:
        srt_content = await srt_file.read()

    # Разбор файла srt в список объектов subtitle
    subtitles = list(srt.parse(srt_content))

    # Преобразуем список нового текста в строки
    new_lines = [line.strip() for line in new_text]

    # Обновляем текст субтитров
    for i, subtitle in enumerate(subtitles):
        if i < len(new_lines):
            subtitle.content = new_lines[i]
        else:
            # Если новый текст закончился, оставляем оригинальный текст
            break

    # Преобразуем обновленные субтитры обратно в строку SRT
    updated_srt_content = srt.compose(subtitles)

    # Асинхронная запись обновленного содержимого в новый файл
    async with aiofiles.open(output_path, 'w', encoding='utf-8') as output_file:
        await output_file.write(updated_srt_content)

    return output_path


async def get_sub_text(subtitles_path):
    subtitles = await get_subtitles_content(subtitles_path)
    video_chunks_text = []
    for chunk in subtitles:
        start, end, text = chunk.start, chunk.end, re.sub(r'\{.*?\}', '', str(chunk.content))
        video_chunks_text.append(text)
    return video_chunks_text