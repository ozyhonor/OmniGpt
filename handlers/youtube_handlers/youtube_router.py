from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from utils.download_from_googledrive import create_and_upload_file
from aiogram import Router, F
from aiogram.types import Message
from utils.video.download_video import download_video
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states.states import WaitingYoutube
from spawnbot import bot
from menu import keyboards, texts
import os
from utils.video.check_size import check_size
from utils.video.split_audio import split_audio
from utils.download_subtitles import download_video_subtitles

import shutil
youtube_router = Router()


@youtube_router.message(F.text == '🚩 Ютуб')
async def create_youtube_subtitles(message: Message):
    db.connect()
    user_id = message.from_user.id

    voice = db.get_voice(user_id)
    rate = db.get_rate(user_id)
    dict_bool = {True: '✅', False: '❌'}
    buttons1 = keyboards.CustomKeyboard.create_youtube_buttons()
    buttons2 = keyboards.CustomKeyboard.inline_youtube_settings()

    await message.answer(f'{texts.future_request_information}', reply_markup=buttons1)
    id_panel = await message.answer(texts.youtube_download_settings.format(dict_bool[db.get_user_settings('download_subtitles', user_id)],
                                                                           dict_bool[db.get_user_settings('download_video', user_id)],
                                                                           dict_bool[db.get_user_settings('download_audio', user_id)]),
                                    reply_markup=buttons2)
    db.update_user_settings('id_youtube_panel', id_panel.message_id, user_id)

    db.disconnect()


@youtube_router.message(F.text == '📥 Скачать')
async def create_download_keyboard(message: Message, state: FSMContext):
    db.connect()

    user_id = message.from_user.id
    await state.set_state(WaitingYoutube.link)
    await message.answer(texts.wait_youtube_link)
    db.disconnect()


@youtube_router.message(WaitingYoutube.link)
async def change_color(message: Message, state: FSMContext):
    db.connect()
    link = message.text
    user_id = message.from_user.id
    subtitles = db.get_user_settings('download_subtitles', user_id)
    video = db.get_user_settings('download_video', user_id)
    audio = db.get_user_settings('download_audio', user_id)
    if subtitles:
        result: bool = await bot.send_chat_action(message.from_user.id, 'typing')
        answer = download_video_subtitles(link, _all_=True)
        file_name = answer + '.txt'
        document = FSInputFile("subtitles/" + file_name)
        await bot.send_message(message.chat.id, 'Субтитры')
        await bot.send_document(message.chat.id, document)
        shutil.rmtree('subtitles')
        os.makedirs('subtitles')
    if video:
        result: bool = await bot.send_chat_action(message.from_user.id, 'typing')
        video_title = download_video(link)
        google_drive_link = create_and_upload_file(dir_path='video', name=video_title)
        await bot.send_message(message.chat.id, 'Видео')
        await bot.send_message(message.chat.id, google_drive_link)
        shutil.rmtree('video')
        os.makedirs('video')
    if audio:

        video_title = download_video(link)
        audio_name = split_audio(video_title)
        audio_path = f'audio_files/{audio_name}'
        await bot.send_message(message.chat.id, 'Аудио')
        if check_size(audio_path):
            google_drive_link = create_and_upload_file(dir_path='audio_files', name=audio_name)
            await bot.send_message(message.chat.id, google_drive_link)
        else:
            audio = FSInputFile(audio_path)
            await bot.send_audio(message.from_user.id, audio=audio)
        shutil.rmtree('video')
        os.makedirs('video')
        shutil.rmtree('audio_files')
        os.makedirs('audio_files')

    await state.clear()
    db.disconnect()



