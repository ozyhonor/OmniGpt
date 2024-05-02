import os
import subprocess


def add_music(video_name, input_video_dir, music, volume):
    music_volume = volume * 0.01
    video_volume = 1 - music_volume
    output_path = 'music_'+video_name
    path_to_video = input_video_dir+"/"+video_name
    command = [
        'ffmpeg', '-i', f"{path_to_video}", '-i', music,
        '-filter_complex',
        f'[0:a]volume={video_volume}[a1];[1:a]volume={music_volume}[a2];[a1][a2]amix=inputs=2[out_a]',
        '-c:v', 'copy', '-map', '0:v:0', '-map', '[out_a]', '-shortest', f"{output_path}"
    ]

    subprocess.run(command, check=True)
    os.remove(path_to_video)
    os.rename(output_path, path_to_video)
    return path_to_video
