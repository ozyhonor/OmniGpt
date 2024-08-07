import subprocess
import string

def split_timestamps(stamps, title):
    piece_path_mp4 = ''
    print(title)
    number = ''.join([i for i in stamps[0] if i in string.digits] + [i for i in stamps[1] if i in string.digits])
    video_output_path = f"TmpVideo/{number}.mp4"
    audio_output_path = f"TmpVideo/{number}.mp3"
    cmd = [
        "ffmpeg",
        "-y",
        "-i", title,
        "-ss", stamps[0],
        "-to", stamps[1],
        "-c", "copy",
        video_output_path
    ]
    # Выполняем команду
    subprocess.run(cmd)
    audio_cmd = [
        "ffmpeg",
        "-y",
        "-i", video_output_path,
        "-q:a", "0",
        "-map", "a",
        audio_output_path
    ]
    # Выполняем команду для извлечения аудио
    subprocess.run(audio_cmd)
    return f'TmpVideo/{number}.mp4'
