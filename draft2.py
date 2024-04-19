import subprocess

def convert_mkv_to_mp4(mkv_file_path, mp4_file_path):
    ffmpeg_command = ['ffmpeg', '-i', mkv_file_path, '-codec:v', 'copy', '-codec:a', 'copy', mp4_file_path]
    try:
        subprocess.check_call(ffmpeg_command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        print(f'Successfully converted {mkv_file_path} to {mp4_file_path}')
    except subprocess.CalledProcessError as error:
        print(f'Error occurred while converting {mkv_file_path} to {mp4_file_path}: {error}')

# Usage example:
mkv_file_path = 'video/gfs1e2.mkv'
mp4_file_path = 'video/gfs1e2.mp4'
convert_mkv_to_mp4(mkv_file_path, mp4_file_path)