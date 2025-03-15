import math
import asyncio
import subprocess
from utils.send_to_sinthesis_request import send_recognize_request
from utils.detect_file_format import detect_file_type
from moviepy import VideoFileClip, AudioFileClip


async def run_ffmpeg_command(cmd):
    """Асинхронная обертка для subprocess."""
    process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    await process.communicate()


async def send_file_to_synthesis(file, resp_synthesis_format='text'):
    file_to_request = file
    format = detect_file_type(file)

    if 'video_' in format:
        format = format.split('_')[1]
        video = VideoFileClip(file)
        file_to_request = file.replace(format, 'mp3')

        # Асинхронное выполнение команды ffmpeg для извлечения аудио из видео
        cmd1 = ["ffmpeg", "-y", "-i", f"{file}", "-vn", "-ab", "192k", "-ac", "2", f"{file_to_request}"]
        await run_ffmpeg_command(cmd1)
        duration = video.duration
    elif 'audio_' in format:
        audio = AudioFileClip(file)
        duration = audio.duration
    else:
        return

    max_duration_seconds = 15 * 60

    if duration <= max_duration_seconds:

        subtitle_file_path = await send_recognize_request(file, future_format=resp_synthesis_format)
        return subtitle_file_path
    else:
        num_pieces = math.ceil(duration / max_duration_seconds)

        for i in range(num_pieces):
            start_time = int(i * max_duration_seconds)
            end_time = int(min((i + 1) * max_duration_seconds, duration))
            print(start_time, '-start', end_time, '-end')
            piece_mp4 = f'piece_{i}.mp4'
            piece_mp3 = f'piece_{i}.mp3'

            piece_path_mp3 = 'subtitles' + '/' + piece_mp3

            cmd3 = ["ffmpeg", "-y", "-i", f"{file_to_request}", "-ss", f"{start_time}", "-to", f"{end_time}", "-c:a",
                    "libmp3lame", "-q:a", "4", f"{piece_path_mp3}"]
            await run_ffmpeg_command(cmd3)

            # Отправляем запрос для транскрипции каждой части
            await send_recognize_request(piece_path_mp3)

        return 'Many'
