import os
import subprocess


def slow_down_speed(name, slow_down=0.6):
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", name,
        "-filter_complex", f"[0:v]setpts={1 + slow_down}*PTS[v];[0:a]atempo={slow_down}[a]",
        "-map", "[v]", "-map", "[a]",
        name.replace("omni_", "slowed")
    ]

    subprocess.run(ffmpeg_command)
    file_name2 = name.replace("omni_", "slowed")

    os.remove(name)
    os.rename(name.replace("omni_", "slowed"), name.replace("slowed", "omni_"))
    return name