import subprocess
import os

# Файл с путями к видеофайлам
input_file = "chunks_video.txt"
output_file = "output_final.mp4"

# Параметры для нормализации видео
video_bitrate = "462k"
audio_bitrate = "128k"
audio_sample_rate = "24000"
audio_channels = "1"

# Функция для приведения видео и аудио к одинаковым параметрам
def normalize_video(video_path, output_path):
    ffmpeg_command = [
        "ffmpeg",
        "-i", video_path,
        "-c:v", "libx264",           # Видео кодек
        "-b:v", video_bitrate,       # Битрейт видео
        "-c:a", "aac",               # Аудио кодек
        "-b:a", audio_bitrate,       # Битрейт аудио
        "-ar", audio_sample_rate,    # Частота дискретизации
        "-ac", audio_channels,       # Каналы аудио (моно)
        output_path
    ]
    subprocess.run(ffmpeg_command)

# Функция для создания списка для склеивания
def create_concatenate_file(video_files):
    with open(input_file, "w") as file:
        for video in video_files:
            file.write(f"file '{video}'\n")

# Приводим все видео файлы к одинаковым параметрам
video_files = []
with open(input_file, "r") as file:
    for line in file:
        video_path = line.strip().replace("file '", "").replace("'", "")
        output_video_path = f"normalized_{os.path.basename(video_path)}"
        normalize_video(video_path, output_video_path)
        video_files.append(output_video_path)

# Создаем файл для склеивания
create_concatenate_file(video_files)

# Склеиваем видео файлы
ffmpeg_command = [
    "ffmpeg",
    "-f", "concat",
    "-safe", "0",
    "-i", input_file,
    "-c:v", "libx264",
    "-c:a", "aac",
    "-strict", "experimental",
    output_file
]
subprocess.run(ffmpeg_command)

print(f"Видео склеено и сохранено как {output_file}")
