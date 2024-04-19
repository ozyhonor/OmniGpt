import subprocess
from utils.video.get_resolution import get_video_resolution
import os
import shutil


def change_resolution_video(title='tmp/omni_video.mp4'):
    resolution = get_video_resolution(title)
    command1 = f"ffmpeg -y -i {title} -vf \"crop=720:{resolution['h']}:{(resolution['w']-720)//2}:0\" -c:a copy TmpVideo/VHQ.mp4"
    subprocess.run(command1)

    command2 = f"ffmpeg -y -i TmpVideo/VHQ.mp4 -vf \"scale=720:1280,setsar=1\" -c:a copy TmpVideo/VHQ2.mp4"
    subprocess.run(command2)

    command3 = f"ffmpeg -y -i TmpVideo/VHQ2.mp4 -vf \"boxblur={0.6*10}:{0.6*10}\" -c:a copy TmpVideo/blurred.mp4"
    subprocess.run(command3)

    command4 = f'ffmpeg -y -i TmpVideo/blurred.mp4 -i TmpVideo/VHQ.mp4 -filter_complex "[0:v][1:v]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[outv]" -map "[outv]" -map 0:a -c:a copy TmpVideo/cropped.mp4'
    subprocess.run(command4)
    os.remove(title)
    os.rename('TmpVideo/cropped.mp4', title)