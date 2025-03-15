import os


def detect_file_type(file_path):
    _, ext = os.path.splitext(file_path)
    # Аудио форматы
    audio_extensions = [
        '.mp3', '.wav', '.ogg', '.flac', '.m4a',
        '.oga', '.aac', '.wma', '.aiff', '.ape', '.alac'
    ]

    # Видео форматы
    video_extensions = [
        '.mp4', '.avi', '.mov', '.mkv', '.webm',
        '.flv', '.wmv', '.mpeg', '.mpg', '.3gp', '.vob', '.ts', '.ogv'
    ]

    if ext.lower() in audio_extensions:
        return f'audio_{ext.lower()}'
    elif ext.lower() in video_extensions:
        return f'video_{ext.lower()}'
    else:
        return 'unknown'