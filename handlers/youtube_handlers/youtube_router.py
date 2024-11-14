from db.database import db
from utils.download_from_googledrive import create_and_upload_file
from aiogram import Router, F
from utils.create_download_link import upload_to_fileio
from aiogram.types import Message
from utils.youtube_downloaders.download_video import download_video_from_youtube
from utils.youtube_downloaders.download_audio import download_audio_from_youtube
from utils.youtube_downloaders.download_subtitles import download_subtitles_from_youtube
from utils.youtube_downloaders.download_subtitles_from_playlist import download_subtitles_from_playlist
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states.states import WaitingYoutube
from spawnbot import bot
from menu import keyboards, texts
import os
from utils.edit_content.check_size import check_size
from utils.edit_content.split_audio import split_audio
from utils.download_subtitles import download_video_subtitles

import shutil
youtube_router = Router()


@youtube_router.message(F.text == '🚩 Ютуб')
async def create_youtube_subtitles(message: Message):
    user_id = message.from_user.id
    dict_bool = {True: '✅', False: '❌'}
    buttons1 = keyboards.CustomKeyboard.create_youtube_buttons()
    buttons2 = keyboards.CustomKeyboard.inline_youtube_settings()

    await message.answer(f'{texts.future_request_information.format('🚩 Ютуб')}', reply_markup=buttons1)
    down_sub = dict_bool[await db.get_user_setting('download_subtitles', user_id)]
    down_vid = dict_bool[await db.get_user_setting('download_video', user_id)]
    down_aud = dict_bool[await db.get_user_setting('download_audio', user_id)]
    down_lang = await db.get_user_setting('download_language_subtitles', user_id)
    id_panel = await message.answer(texts.youtube_download_settings.format(down_sub,
                                                                           down_vid,
                                                                           down_aud,
                                                                           down_lang),
                                    reply_markup=buttons2)
    await db.update_user_setting('id_youtube_panel', id_panel.message_id, user_id)



@youtube_router.message(F.text == '📥 Скачать')
async def create_download_keyboard(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(WaitingYoutube.link)
    await message.answer(texts.wait_youtube_link)


@youtube_router.message(F.text == '💽 Плейлист')
async def create_download_keyboard(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.set_state(WaitingYoutube.playlist)
    await message.answer(texts.wait_youtube_playlist_link)


@youtube_router.message(WaitingYoutube.playlist)
async def download_content(message: Message, state: FSMContext):
    link = message.text
    user_id = message.from_user.id
    await bot.send_chat_action(message.from_user.id, 'typing')
    subtitle_path = await download_subtitles_from_playlist(link, user_id)
    if check_size(subtitle_path):  # content > 25 mb
        fileio_link = await upload_to_fileio(subtitle_path)
        await bot.send_message(user_id, fileio_link)
    else:
        combined_sub = FSInputFile(subtitle_path)
        await bot.send_document(chat_id=user_id, document=combined_sub)
    shutil.rmtree('subtitles')
    os.makedirs('subtitles')


@youtube_router.message(WaitingYoutube.link)
async def download_content(message: Message, state: FSMContext):
    link = message.text
    user_id = message.from_user.id
    subtitles = await db.get_user_setting('download_subtitles', user_id)
    video = await db.get_user_setting('download_video', user_id)
    audio = await db.get_user_setting('download_audio', user_id)
    if subtitles:
        await bot.send_chat_action(message.from_user.id, 'typing')
        subtitle_path = await download_subtitles_from_youtube(link, user_id)
        subtitles_file = FSInputFile(subtitle_path)
        print(subtitle_path)
        await bot.send_document(message.chat.id, subtitles_file)
        shutil.rmtree('subtitles')
        os.makedirs('subtitles')
    if video:
        await bot.send_chat_action(user_id, 'upload_video')
        video_path = await download_video_from_youtube(link, user_id)
        if check_size(video_path): # content > 25 mb
            fileio_link = await upload_to_fileio(video_path)
            await bot.send_message(user_id, fileio_link)
        else:
            video = FSInputFile(video_path)
            await bot.send_video(chat_id=user_id, video=video)
        shutil.rmtree('video')
        os.makedirs('video')
    if audio:
        await bot.send_chat_action(user_id, 'upload_audio')
        audio_path = await download_audio_from_youtube(link)
        if check_size(audio_path):
            fileio_link = await upload_to_fileio(audio_path)
            await bot.send_message(user_id, fileio_link)
        else:
            audio = FSInputFile(audio_path)
            await bot.send_audio(chat_id=user_id, audio=audio)
        shutil.rmtree('audio_files')
        os.makedirs('audio_files')

    await state.clear()



