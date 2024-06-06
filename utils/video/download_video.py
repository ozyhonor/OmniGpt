import re
import subprocess
import string
from config_reader import yt_mail_for_downloading, yt_pass_for_downloading


def download_video(url: str, lang='ru') -> str:

    comma = f'yt-dlp --print "%(title)s" {url}'

    output = subprocess.check_output(comma, shell=True)
    title = output.decode('utf-8').strip()

    trans_table = str.maketrans('', '', string.punctuation)
    title = title.translate(trans_table).replace(' ', '_').lower()

    video_command = (f'yt-dlp '
               f'--username "{yt_mail_for_downloading}" '
               f'--password "{yt_pass_for_downloading}" '
               f'-o "video/{title}.mp4" '
               f'-f "bestvideo[ext=mp4]+bestaudio[ext=mp3]/best[ext=mp4]" "{url}"')

    audio_command = (f'yt-dlp '
                    f'--username "{yt_mail_for_downloading}" '
                    f'--password "{yt_pass_for_downloading}" '
                    f'-o "video/{title}.mp3" '
                    f'-x --audio-format mp3 '
                    f'"{url}"')

    subprocess.run(audio_command, check=True, shell=True)

    subprocess.run(video_command, check=True, shell=True)

    return title+'.mp4'