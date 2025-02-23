from db.database import db
from utils.download_from_googledrive import create_and_upload_file
from aiogram import Router, F
from utils.edit_content.local_requests.get_subtitles import send_recognize_request
from utils.create_download_link import upload_file_to_gDisk
from aiogram.types import Message
from utils.youtube_downloaders.download_video import download_video_from_youtube
from utils.youtube_downloaders.download_audio import download_audio_from_youtube
from utils.youtube_downloaders.download_subtitles import download_subtitles_from_youtube
from utils.youtube_downloaders.download_subtitles_from_playlist import download_subtitles_from_playlist
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states.states import WaitingYoutube
from spawnbot import bot
from utils.edit_content.video_editor import get_video_duration, calculate_length, trim_by_timecode
from aiogram import types
from menu import keyboards, texts
import os
import math
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
    split_play_list = await db.get_user_setting('split_play_list', user_id)
    down_lang = await db.get_user_setting('download_language_subtitles', user_id)
    id_panel = await message.answer(texts.youtube_download_settings.format(down_sub,
                                                                           down_vid,
                                                                           down_aud,
                                                                           down_lang,
                                                                           split_play_list),
                                    reply_markup=buttons2)
    await db.update_user_setting('id_youtube_panel', id_panel.message_id, user_id)


@youtube_router.callback_query(lambda callback_query: callback_query.data.startswith('need_gen_sub:'))
async def generate_subtitles(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    message_text_from_message_with_callback_query = callback_query.message.text
    link = message_text_from_message_with_callback_query.split('видео ')[1]
    answer = callback_query.data.split(':')[1]
    all_files = []
    if answer == "✅ Да":
        await bot.send_message(user_id, 'создаю')
        audio_path = await download_audio_from_youtube(link)
        duration = await get_video_duration(audio_path)
        num_pieces = math.ceil(duration / 833)
        audio_path_by_ten_minutes = []
        for number_video_part in range(num_pieces):
            ten_minutes_timecode = await calculate_length(number_video_part, duration)
            start, end = ten_minutes_timecode['start'], ten_minutes_timecode['end']

            if duration > end:
                ten_minute_audio = await trim_by_timecode(audio_path, start, end)  # ?
                audio_path_by_ten_minutes.append(ten_minute_audio)
            else:
                audio_path_by_ten_minutes.append(audio_path)

            video_to_process = audio_path_by_ten_minutes[number_video_part]
            subtitle_path = await send_recognize_request(audio_path, 'smart')
            all_files.append(subtitle_path)


        output_file_path = "txt files/gensub.txt"
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for file_path in all_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as input_file:
                        content = input_file.read()
                        output_file.write(content)
                        output_file.write('\n\n')
                else:
                    print(f"Файл {file_path} не найден.")
        subtitles_file = FSInputFile(output_file_path)
        await bot.send_document(user_id, subtitles_file)
        shutil.rmtree('subtitles')
        os.makedirs('subtitles')

    else:
        await bot.delete_message(user_id,message_id)

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
    target_lang = await db.get_user_setting('download_language_subtitles', user_id)
    split_simbol = await db.get_user_setting('split_play_list', user_id)
    if split_simbol == '❌':
        split_simbol = ''
    await bot.send_chat_action(message.from_user.id, 'typing')
    subtitle_path = await download_subtitles_from_playlist(link, user_id, language=target_lang, message=message, split_simbol=split_simbol)
    if check_size(subtitle_path):  # content > 25 mb
        fileio_link = await upload_file_to_gDisk(subtitle_path)
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
        language = await db.get_user_setting('download_language_subtitles', user_id)
        subtitle_path = await download_subtitles_from_youtube(link, user_id, language)
        subtitles_file = FSInputFile(subtitle_path)
        print(subtitle_path)
        await bot.send_document(message.chat.id, subtitles_file)
        shutil.rmtree('subtitles')
        os.makedirs('subtitles')
    if video:
        await bot.send_chat_action(user_id, 'upload_video')
        video_path = await download_video_from_youtube(link, user_id)
        if check_size(video_path): # content > 25 mb
            fileio_link = await upload_file_to_gDisk(video_path)
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
            fileio_link = await upload_file_to_gDisk(audio_path)
            await bot.send_message(user_id, fileio_link)
        else:
            audio = FSInputFile(audio_path)
            await bot.send_audio(chat_id=user_id, audio=audio)
        shutil.rmtree('audio_files')
        os.makedirs('audio_files')

    await state.clear()



