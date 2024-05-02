from moviepy.editor import VideoFileClip
import os
import math
from moviepy.editor import AudioFileClip
from pydub import AudioSegment
from utils.video.get_subtitles import send_recognize_request
from utils.convert_json_to_srt import json_to_srt
import subprocess
from moviepy.editor import VideoFileClip
import shutil

def split_video_and_get_subtitles(smart, video_path, output_dir, max_duration_minutes=15, words_per_chunk=6):

    video = VideoFileClip(video_path)
    audio_path = video_path.replace('mp4', 'mp3')
    cmd1= ["ffmpeg", "-y", f"-i {video_path}", "-vn", f"-ab 192k", "-ac 2", f"{audio_path}"]
    subprocess.run(cmd1, shell=True)

    duration = video.duration
    max_duration_seconds = max_duration_minutes * 60

    if duration <= max_duration_seconds:
        # Если видео короче 15 минут, копируем его в папку и сохраняем отдельно mp3 файл

        shutil.copyfile(video_path, output_dir + '/piece_0.mp4')
        shutil.copyfile(audio_path, output_dir + '/piece_0.mp3')
        send_recognize_request( output_dir + '/piece_0.mp3', smart=smart)
        json_file = output_dir + '/piece_0.json'
        srt_file = output_dir + '/piece_0.srt'
        json_to_srt(smart, json_file, srt_file, words_per_chunk)
        return 'Solo'
    else:
        # Если видео длиннее 15 минут, делим его на фрагменты по 15 минут
        num_pieces = math.ceil(duration / max_duration_seconds)

        for i in range(num_pieces):
            start_time = float(f"{i * max_duration_seconds:.2f}")
            end_time = float(f"{min((i + 1) * max_duration_seconds, duration):.2f}")

            piece_mp4 = f'piece_{i}.mp4'
            piece_mp3 = f'piece_{i}.mp3'
            piece_path_mp4 = output_dir+ '/' + piece_mp4 # TmpVideo/piece_0.mp4
            piece_path_mp3 = output_dir+ '/' + piece_mp3

            # Используем moviepy для разделения видео
            cmd2 = ["ffmpeg", "-y", "-i", f"{video_path}", f"-ss {start_time}", f"-to {end_time}", "-c", "copy", f"{piece_path_mp4}"]
            subprocess.run(cmd2, shell=True)

            # Используем ffmpeg для разделения аудио
            cmd3 = ["ffmpeg", "-y", "-i", f"{audio_path}", f"-ss {start_time}", f"-to {end_time}", "-c:a", "libmp3lame", "-q:a 4" f"{piece_path_mp3}"]
            subprocess.run(cmd3, shell=True)

            send_recognize_request(output_dir + f'/piece_{i}.mp3', smart=smart)
            json_file = piece_path_mp3.replace(".mp3", ".json")
            srt_file = piece_path_mp3.replace(".mp3", ".srt")
            words_per_chunk = 6
            json_to_srt(smart, json_file, srt_file, words_per_chunk)
        return 'Many'