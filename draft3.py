import subprocess

def add_music(video_path, music, output_path='output.mp4'):
    command = [
        'ffmpeg', '-i', f"{video_path}", '-i', music,
        '-filter_complex',
        '[0:a]volume=0.6[a1];[1:a]volume=0.4[a2];[a1][a2]amix=inputs=2[out_a]',
        '-c:v', 'copy', '-map', '0:v:0', '-map', '[out_a]', '-shortest', f"{output_path}"
    ]

    subprocess.run(command, check=True)
    os.remove(title)
    os.rename('TmpVideo/cropped.mp4', title)



