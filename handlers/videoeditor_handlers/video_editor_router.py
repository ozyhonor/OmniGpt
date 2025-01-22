from spawnbot import bot
from aiogram import Router, F
from  db.database import db
from aiogram.types import Message
from states.states import WaitingStateDoVideo
from aiogram.fsm.context import FSMContext
import re
from utils.edit_content.split_video_audio import split_video_and_get_subtitles
from menu.keyboards import CustomKeyboard
from utils.create_download_link import upload_to_fileio
import os
from utils.edit_content.slow_down_speed import slow_down_speed
from aiogram.types.input_file import FSInputFile
import shutil
from utils.youtube_downloaders.download_video import download_video_from_youtube
from utils.check_interesting_moment import choose_good_moment
from utils.edit_content.clear_directory import clear_directory
from utils.edit_content.check_size import check_size
from utils.edit_content.convert_to_short_resol import change_resolution_video
from utils.download_from_googledrive import create_and_upload_file
from utils.edit_content.create_video import VideoEditor, combine_video_chunks
from utils.edit_content.split_video import split_timestamps
from utils.edit_content.add_music import add_music
from utils.edit_content.video_editor import process_video
from utils.download_subtitles import download_video_subtitles
from utils.gpt_requests import chunks_request
from utils.split_text_for_gpt import split_text
from utils.decode_any_format import detect_file_format
from menu import texts

video_editor_router = Router()


@video_editor_router.message(F.text == '🛠️ Создать видео')
async def create_video_handler(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается youtube ссылка или файл формата mp4.', reply_markup=markup)
    await state.set_state(WaitingStateDoVideo.do_video)


@video_editor_router.message(WaitingStateDoVideo.do_video)
async def process_video_handler(message: Message, state: FSMContext):
    '''
    скачать
    обоаботать
    отдать
    '''
    user_id = message.from_user.id
    url_video = message.text

    #Скачать
    await message.answer('Скачиваю видео...')
    video_path = await download_video_from_youtube(url_video, user_id)
    sanitized_video_path = re.sub(r"[^A-Za-zА-Яа-я0-9/\\\.]", "_", video_path)
    if video_path != sanitized_video_path:
        os.rename(video_path, sanitized_video_path)
        video_path = sanitized_video_path

    #Обработать
    await message.answer('Обрабатываю видео')
    new_video_path = await process_video(video_path, user_id, message)

    if check_size(new_video_path):
        link = await upload_to_fileio(new_video_path)
        await bot.send_message(chat_id=user_id, text=f'Видео скачено!\n{link}')
    else:
        video = FSInputFile(new_video_path)
        await bot.send_video(chat_id=user_id, video=video)

    os.remove(new_video_path)

    await state.clear()


