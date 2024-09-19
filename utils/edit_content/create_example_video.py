import subprocess
from fontTools.ttLib import TTFont
import os
from db.database import db
import asyncio
from spawnbot import bot
from aiogram.types.input_file import FSInputFile


import os
import subprocess

async def create_example_video_async(user_id):
    db.connect()
    font = db.get_font(user_id)
    subtitles = db.get_subtitles(user_id)
    font_size = db.get_size(user_id)
    font_color = db.get_color(user_id)
    shadow_color = db.get_shadow_color(user_id)
    shadow_size = db.get_shadow_size(user_id)
    outline_size = db.get_outline_size(user_id)
    outline_color = db.get_outline_color(user_id)
    outline = db.get_outline(user_id)
    shadow = db.get_shadow(user_id)

    example_image = os.path.realpath('example/edit_content.mp4')
    subtitle_file = 'example/example.srt'
    output_file = 'example/example.mp4'
    font_file = 'fonts/' + font
    font_ = TTFont(font_file)
    font_name = font_['name'].names[1].toUnicode()
    if outline:
        outline_str = f",OutlineColour={outline_color},OutlineSize={outline_size}"
    else:
        outline_str = ""

    if shadow:
        shadow_str = f",ShadowColour={shadow_color},ShadowXOffset={shadow_size},ShadowYOffset={shadow_size}"
    else:
        shadow_str = ""
    command = [
        "ffmpeg",
        "-y",
        "-i", example_image,
        "-vf",
        f"subtitles={subtitle_file}:force_style='FontName={font_name},FontSize={font_size},PrimaryColour={font_color}{shadow_str}{outline_str}'",
        "-c:a", "copy",
        output_file
    ]
    print(command)
    # выполняем команду ffmpeg
    subprocess.run(command, check=True)
    video = FSInputFile(f'example/example.mp4')

    # отправка видео асинхронно
    await (bot.send_video(user_id, video))
    os.remove(f'example/example.mp4')
    db.disconnect()


