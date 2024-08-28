import os
import subprocess


"""
ffmpeg -i input.mp4 -vf "setpts=(PTS-STARTPTS)/0.5" -af atempo=0.5 output02.mp4
"""
def slow_down_speed(name, slow_down):

    slow_setpts = {0.5: 2, 0.8: 1.25, 0.625: 1.6}[slow_down]
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", name,
        "-filter_complex", f"[0:v]setpts={slow_setpts}*PTS[v];[0:a]atempo={slow_down}[a]",
        "-map", "[v]",
        "-map", "[a]",
        name.replace('/', '/slowed_')
    ]

    subprocess.run(ffmpeg_command)
    file_name2 = name.replace('/', '/slowed_')

    os.remove(name)
    os.rename(file_name2, name)
    return name
