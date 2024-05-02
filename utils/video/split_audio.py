import subprocess
from moviepy.editor import VideoFileClip
import shutil


def split_audio(video_name):

    audio_path = video_name.replace('mp4', 'mp3')
    subprocess.run(f"ffmpeg -i video/{video_name} -vn -ab 192k -ac 2 audio_files/{audio_path}", shell=True)
    return audio_path
