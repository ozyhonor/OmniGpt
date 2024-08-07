from aiogram import Router, F
from aiogram.types import Message
from utils.video.create_translate import create_translate_text
from db.database import db
from aiogram import Router, F
from aiogram.types import Message
import states.states
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states.states import WaitingStateGpt
from aiogram.fsm.context import FSMContext
from menu import keyboards, texts
from spawnbot import bot
from aiogram import types
from spawnbot import bot
from aiogram import Router
from  db.database import db
from aiogram.types import Message
from states.states import WaitingStateTranslator
from aiogram.fsm.context import FSMContext
from menu import texts
import os
from aiogram import types
from utils.video.create_example_video import create_example_video_async
from utils.is_color import is_hex_color
from menu.keyboards import CustomKeyboard
from utils.decode_any_format import detect_file_format
from utils.split_text_for_gpt import split_text


translator_router = Router()






@translator_router.message(F.text == '🔄 Перевод')
async def create_gpt_request_for_request(message: Message):
    db.connect()
    languages = [
            {'code': 'en', 'flag': '🇬🇧', 'name': 'English'},
            {'code': 'es', 'flag': '🇪🇸', 'name': 'Spanish'},
            {'code': 'fr', 'flag': '🇫🇷', 'name': 'French'},
            {'code': 'ru', 'flag': '🇷🇺', 'name': 'Russian'},
            {'code': 'zh-cn', 'flag': '🇨🇳', 'name': 'Chinese (Simplified)'},
            {'code': 'ar', 'flag': '🇸🇦', 'name': 'Arabic'},
            {'code': 'pt', 'flag': '🇵🇹', 'name': 'Portuguese'},
            {'code': 'de', 'flag': '🇩🇪', 'name': 'German'},
            {'code': 'ja', 'flag': '🇯🇵', 'name': 'Japanese'},
            {'code': 'hi', 'flag': '🇮🇳', 'name': 'Hindi'},
            {'code': 'it', 'flag': '🇮🇹', 'name': 'Italian'},
            {'code': 'ko', 'flag': '🇰🇷', 'name': 'Korean'},
        ]
    user_id = message.from_user.id
    dest_lang = db.get_user_settings('dest_lang',user_id)
    for language in languages:
        if language['code'].lower() == dest_lang.lower():
            flag = language['flag']
    setting = db.get_settings(user_id)

    markup_inline = keyboards.CustomKeyboard.inline_translated_languages_for_translator()
    markup_reply = keyboards.CustomKeyboard.create_translator_buttons()

    await message.answer(f'{texts.future_request_information}', reply_markup=markup_reply)
    id_translator_panel = await message.answer(f'<b><blockquote>Перевести на {dest_lang} {flag}</blockquote></b>\n<pre>➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖</pre>', reply_markup=markup_inline)
    id_translator_panel = id_translator_panel.message_id
    db.update_user_settings('translator_id_panel', id_translator_panel, user_id)
    db.disconnect()


@translator_router.callback_query(lambda callback_query: callback_query.data.startswith('translator_dest_lang:'))
async def process_overlap_value_button(callback_query: types.CallbackQuery):
    db.connect()
    dest = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_user_settings('translator_id_panel', user_id)
    db.update_user_settings(key='dest_lang', value=dest, user_id=user_id)
    languages = [
            {'code': 'en', 'flag': '🇬🇧', 'name': 'English'},
            {'code': 'es', 'flag': '🇪🇸', 'name': 'Spanish'},
            {'code': 'fr', 'flag': '🇫🇷', 'name': 'French'},
            {'code': 'ru', 'flag': '🇷🇺', 'name': 'Russian'},
            {'code': 'zh-cn', 'flag': '🇨🇳', 'name': 'Chinese (Simplified)'},
            {'code': 'ar', 'flag': '🇸🇦', 'name': 'Arabic'},
            {'code': 'pt', 'flag': '🇵🇹', 'name': 'Portuguese'},
            {'code': 'de', 'flag': '🇩🇪', 'name': 'German'},
            {'code': 'ja', 'flag': '🇯🇵', 'name': 'Japanese'},
            {'code': 'hi', 'flag': '🇮🇳', 'name': 'Hindi'},
            {'code': 'it', 'flag': '🇮🇹', 'name': 'Italian'},
            {'code': 'ko', 'flag': '🇰🇷', 'name': 'Korean'},
        ]
    dest = db.get_user_settings('dest_lang',user_id)
    for language in languages:
        if language['code'].lower() == dest.lower():
            flag = language['flag']
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=f'<b><blockquote>Перевести на {dest} {flag}</blockquote></b>\n<pre>➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖</pre>')
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=keyboards.CustomKeyboard.inline_translated_languages_for_translator())
    db.disconnect()


@translator_router.message(F.text == '🗃 Файл')
async def process_message_gpt_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    await state.set_state(WaitingStateTranslator.file_translate)
    await bot.send_message(user_id, '<b>Ожидается файловый запрос</b>')


@translator_router.message(WaitingStateTranslator.file_translate)
async def process_file_gpt_request(message: Message, state: FSMContext, settings=None) -> None:
    """
    """
    db.connect()
    result: bool = await bot.send_chat_action(message.from_user.id, 'upload_document')
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    main_file_name = ['txt files/', message.document.file_name]
    await bot.download_file(file_path, main_file_name[0]+main_file_name[1])

    text = detect_file_format(main_file_name[0]+main_file_name[1])
    file_name = main_file_name[1].rsplit('.', 1)[0] + '.txt'
    chunks = split_text(text)
    dest = db.get_user_settings('dest_lang', message.from_user.id)
    new_ = []
    await message.answer(f'<b>Количество запросов в файле</b>: {len(chunks)}\n')
    for _ in chunks:
        a = create_translate_text(_, dest=dest)
        print(a)
        new_.append(a)
    with open(f"txt files/Omni_{file_name}", "w", encoding="utf-8") as file:
        for answer in new_ or 'OmniBot':
            file.write(answer + "\n")
    await message.answer(texts.water_mark_omnigpt.format(answer[0]))

    file_name = main_file_name[1].rsplit('.', 1)[0] + '.txt'
    document = FSInputFile(f"txt files/Omni_{file_name}")
    await bot.send_document(message.chat.id, document)

    os.remove(f'txt files/Omni_{file_name}')
    os.remove(f'{main_file_name[0]+main_file_name[1]}')
    db.disconnect()
    await state.clear()


@translator_router.message(F.text == '◀️ Назад')
async def go_to_main_menu(message: Message, state: FSMContext):

    markup = keyboards.CustomKeyboard.create_reply_main_menu()
    await message.answer('<b>Главное меню</b>', reply_markup=markup)
    await state.clear()
