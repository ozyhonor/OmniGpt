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
    db.connect()
    changed_setting = callback_query.data.split(':')[1]
    dict_bool = {True : '✅', False: '❌'}
    transcription = {'subtitles': 'субтитры', 'video': 'видео', 'audio': 'аудио'}
    user_id = callback_query.from_user.id
    markup = keyboards.CustomKeyboard.inline_cancel()
    id_panel = db.get_user_settings('id_youtube_panel', user_id)
    bool_changed_setting: bool = not(db.get_user_settings(f'download_{changed_setting}', user_id))
    db.update_user_settings(f'download_{changed_setting}', bool_changed_setting, user_id)
    await callback_query.answer(f'Скачать {transcription[changed_setting]} {dict_bool[bool_changed_setting]}')
    markup = keyboards.CustomKeyboard.inline_youtube_settings()
    await bot.edit_message_text(chat_id=user_id, message_id=id_panel, text=reload_settings(user_id))
    await bot.edit_message_reply_markup(user_id, id_panel, reply_markup=markup)
    db.disconnect()



def reload_settings(user_id):
    db.connect()
    dict_bool = {True: '✅', False: '❌'}
    new_settings = texts.youtube_download_settings.format(dict_bool[db.get_user_settings('download_subtitles', user_id)],
                                                 dict_bool[db.get_user_settings('download_video', user_id)],
                                                      dict_bool[db.get_user_settings('download_audio', user_id)])
    db.disconnect()
    return new_settings