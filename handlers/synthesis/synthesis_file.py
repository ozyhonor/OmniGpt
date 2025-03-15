import traceback
from aiogram.types.input_file import FSInputFile
import os
from aiogram import Router, F
from aiogram.types import Message, ContentType
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingStateSynthesis
from spawnbot import bot
from aiogram.types import InputMediaPhoto
from menu import texts
from utils.synthesis_file import send_file_to_synthesis
from utils.latex_to_unicode import convert_latex_to_unicode
import re
from datetime import datetime
from utils.download_picture_from_gpt import download_images
from utils.picture_requests import create_solo_photo


synthesis_file = Router()

@synthesis_file.message(F.text == '💾 Файл')
async def process_message_sythesis_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(WaitingStateSynthesis.file)
    user_id = message.from_user.id
    await bot.send_message(user_id, '<b>Ожидается файловый запрос</b>')


@synthesis_file.message(WaitingStateSynthesis.file)
async def go_synthesis_file_request(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id

    if message.content_type == ContentType.AUDIO:
        file_id = message.audio.file_id
        file_type = "audio"
        download_dir = "audio_files"
    elif message.content_type == ContentType.VOICE:
        file_id = message.voice.file_id
        file_type = "voice"
        download_dir = "audio_files"
    elif message.content_type == ContentType.VIDEO:
        file_id = message.video.file_id
        file_type = "video"
        download_dir = "video_files"
    else:
        await message.answer("Пожалуйста, отправьте аудио, видео или голосовое сообщение.")
        return

    resp_format = await db.get_user_setting('synthesis_response_format', user_id)

    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    print(file_type)
    print(file_path)
    print(file_info)

    downloaded_file = await bot.download_file(file_path)

    file_name = os.path.basename(file_path)
    if file_type == "video" and not file_name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        file_name += '.mp4'

    os.makedirs(download_dir, exist_ok=True)

    save_path = os.path.join(download_dir, file_name)
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file.getvalue())

    await message.bot.send_chat_action(user_id, 'typing')

    subtitle_file_path = await send_file_to_synthesis(save_path, resp_synthesis_format=resp_format)
    document = FSInputFile(subtitle_file_path)
    await bot.send_document(message.chat.id, document)

    try:
        os.remove(subtitle_file_path)
        os.remove(save_path)
    except Exception as e:
        print(f"Error cleaning up files: {e}")

    await state.clear()
