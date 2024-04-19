import subprocess
import string
stamps = ['1:23','3:22']
number = ''.join([i for i in stamps[0] if i in string.digits] + [i for i in stamps[1] if i in string.digits])
print(number)
def split_timestamps(stamps, title):
    piece_path_mp4 = ''
    number = ''.join([i for i in stamps[0] if i in string.digits] + [i for i in stamps[1] if i in string.digits])
    cmd = f"ffmpeg -i {title} -ss {stamps[0]} -to {stamps[1]} -c copy TmpVideo/{number}.mp4"
    subprocess.run(cmd, shell=True)
    print(stamps, number)
    return f'TmpVideo/{number}.mp4'