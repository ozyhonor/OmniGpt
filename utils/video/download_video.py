import re
import subprocess
import string


def download_video(url: str, lang='ru') -> str:

    comma = f'yt-dlp --print "%(title)s" {url}'

    output = subprocess.check_output(comma, shell=True)
    title = output.decode('utf-8').strip()

    trans_table = str.maketrans('', '', string.punctuation)
    title = title.translate(trans_table).replace(' ', '_').lower()

    command = (f'yt-dlp '
               f'--username "robertswst45ur@gmail.com" '
               f'--password "dNn4zIDP9p" '
               f'-o "video/{title}.mp4" '
               f'-f "bestvideo[ext=mp4]+bestaudio[ext=mp3]/best[ext=mp4]" "{url}"')

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    return title+'.mp4'