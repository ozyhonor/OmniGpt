from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingStartSpeech
from spawnbot import bot
from menu import keyboards, texts
from aiogram import types


youtube_settings_router = Router()


@youtube_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('download_from_yt:'))
async def process_music(callback_query: types.CallbackQuery):
    changed_setting = callback_query.data.split(':')[1]
    dict_bool = {True : '✅', False: '❌'}
    transcription = {'download_subtitles': 'субтитры', 'download_video': 'видео', 'download_audio': 'аудио'}
    user_id = callback_query.from_user.id
    markup = keyboards.CustomKeyboard.inline_cancel()
    id_panel = await db.get_user_setting('id_youtube_panel', user_id)
    bool_changed_setting: bool = not(await db.get_user_setting(f'{changed_setting}', user_id))
    await db.update_user_setting(f'{changed_setting}', bool_changed_setting, user_id)
    await callback_query.answer(f'Скачать {transcription[changed_setting]} {dict_bool[bool_changed_setting]}')
    markup = keyboards.CustomKeyboard.inline_youtube_settings()
    new_text_settings = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=id_panel, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, id_panel, reply_markup=markup)


@youtube_settings_router.callback_query(lambda callback_query: callback_query.data =='back_language_youtube')
async def back_subtitles_language_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    id_panel = await db.get_user_setting('id_youtube_panel', user_id)
    markup = keyboards.CustomKeyboard.inline_youtube_settings()
    await bot.edit_message_reply_markup(user_id, id_panel, reply_markup=markup)


@youtube_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('download_subtitles_language:'))
async def open_subtitles_language_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    changed_setting = callback_query.data.split(':')[1]
    id_panel = await db.get_user_setting('id_youtube_panel', user_id)
    await db.update_user_setting('download_language_subtitles', changed_setting, user_id)
    new_text_settings = await reload_settings(user_id)

    markup_main_menu = keyboards.CustomKeyboard.inline_youtube_settings()

    await bot.edit_message_text(chat_id=user_id, message_id=id_panel, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, id_panel, reply_markup=markup_main_menu)



@youtube_settings_router.callback_query(lambda callback_query: callback_query.data =='download_subtitles_language')
async def open_subtitles_language_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    id_panel = await db.get_user_setting('id_youtube_panel', user_id)
    markup = keyboards.CustomKeyboard.inline_translated_languages_for_download_subtitles()
    await bot.edit_message_reply_markup(user_id, id_panel, reply_markup=markup)

async def reload_settings(user_id):
    subtitles = await db.get_user_setting('download_subtitles', user_id)
    video = await db.get_user_setting('download_video', user_id)
    sub_language = await db.get_user_setting('download_language_subtitles', user_id)
    audio = await db.get_user_setting('download_audio', user_id)
    dict_bool = {True: '✅', False: '❌'}
    new_settings = texts.youtube_download_settings.format(dict_bool[subtitles],
                                                 dict_bool[video],
                                                      dict_bool[audio],
                                                          sub_language)

    return new_settings