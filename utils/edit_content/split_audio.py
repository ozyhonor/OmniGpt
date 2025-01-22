import subprocess


def split_audio(video_name):

    audio_path = video_name.replace('mp4', 'mp3')
    command = ["ffmpeg",
               "-y",
               "-i",
               f"video/{video_name}",
               "-vn",
               "-ab 192k",
               "-ac 2",
               f"audio_files/{audio_path}"]
    subprocess.run(command, shell=True)
    return audio_path
