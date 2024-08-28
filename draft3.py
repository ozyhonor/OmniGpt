import asyncio


async def replace_audio(video_path, audio_path, output_path):
    command = [
        'ffmpeg',
        '-i', audio_path,  # Новая аудиодорожка
        '-i', video_path,  # Оригинальное видео
        '-shortest',       # Обрезка видео до длины аудиодорожки
        output_path        # Путь для сохранения нового видеофайла
    ]

    # Запуск команды ffmpeg в асинхронном режиме
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Ожидание завершения процесса и получение вывода
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"Video created successfully: {output_path}")
    else:
        print(f"Error occurred: {stderr.decode()}")