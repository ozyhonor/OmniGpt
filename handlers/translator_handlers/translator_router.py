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
        {'code': 'af', 'flag': '🇿🇦', 'name': 'Afrikaans'},
        {'code': 'ar', 'flag': '🇸🇦', 'name': 'Arabic'},
        {'code': 'hy', 'flag': '🇦🇲', 'name': 'Armenian'},
        {'code': 'az', 'flag': '🇦🇿', 'name': 'Azerbaijani'},
        {'code': 'be', 'flag': '🇧🇾', 'name': 'Belarusian'},
        {'code': 'bs', 'flag': '🇧🇦', 'name': 'Bosnian'},
        {'code': 'bg', 'flag': '🇧🇬', 'name': 'Bulgarian'},
        {'code': 'ca', 'flag': '🇪🇸', 'name': 'Catalan'},
        {'code': 'zh-cn', 'flag': '🇨🇳', 'name': 'Chinese (Simplified)'},
        {'code': 'hr', 'flag': '🇭🇷', 'name': 'Croatian'},
        {'code': 'cs', 'flag': '🇨🇿', 'name': 'Czech'},
        {'code': 'da', 'flag': '🇩🇰', 'name': 'Danish'},
        {'code': 'nl', 'flag': '🇳🇱', 'name': 'Dutch'},
        {'code': 'en', 'flag': '🇬🇧', 'name': 'English'},
        {'code': 'et', 'flag': '🇪🇪', 'name': 'Estonian'},
        {'code': 'fi', 'flag': '🇫🇮', 'name': 'Finnish'},
        {'code': 'fr', 'flag': '🇫🇷', 'name': 'French'},
        {'code': 'gl', 'flag': '🇪🇸', 'name': 'Galician'},
        {'code': 'de', 'flag': '🇩🇪', 'name': 'German'},
        {'code': 'el', 'flag': '🇬🇷', 'name': 'Greek'},
        {'code': 'he', 'flag': '🇮🇱', 'name': 'Hebrew'},
        {'code': 'hi', 'flag': '🇮🇳', 'name': 'Hindi'},
        {'code': 'hu', 'flag': '🇭🇺', 'name': 'Hungarian'},
        {'code': 'is', 'flag': '🇮🇸', 'name': 'Icelandic'},
        {'code': 'id', 'flag': '🇮🇩', 'name': 'Indonesian'},
        {'code': 'it', 'flag': '🇮🇹', 'name': 'Italian'},
        {'code': 'ja', 'flag': '🇯🇵', 'name': 'Japanese'},
        {'code': 'kn', 'flag': '🇮🇳', 'name': 'Kannada'},
        {'code': 'kk', 'flag': '🇰🇿', 'name': 'Kazakh'},
        {'code': 'ko', 'flag': '🇰🇷', 'name': 'Korean'},
        {'code': 'lv', 'flag': '🇱🇻', 'name': 'Latvian'},
        {'code': 'lt', 'flag': '🇱🇹', 'name': 'Lithuanian'},
        {'code': 'mk', 'flag': '🇲🇰', 'name': 'Macedonian'},
        {'code': 'ms', 'flag': '🇲🇾', 'name': 'Malay'},
        {'code': 'mr', 'flag': '🇮🇳', 'name': 'Marathi'},
        {'code': 'mi', 'flag': '🇳🇿', 'name': 'Maori'},
        {'code': 'ne', 'flag': '🇳🇵', 'name': 'Nepali'},
        {'code': 'no', 'flag': '🇳🇴', 'name': 'Norwegian'},
        {'code': 'fa', 'flag': '🇮🇷', 'name': 'Persian'},
        {'code': 'pl', 'flag': '🇵🇱', 'name': 'Polish'},
        {'code': 'pt', 'flag': '🇵🇹', 'name': 'Portuguese'},
        {'code': 'ro', 'flag': '🇷🇴', 'name': 'Romanian'},
        {'code': 'ru', 'flag': '🇷🇺', 'name': 'Russian'},
        {'code': 'sr', 'flag': '🇷🇸', 'name': 'Serbian'},
        {'code': 'sk', 'flag': '🇸🇰', 'name': 'Slovak'},
        {'code': 'sl', 'flag': '🇸🇮', 'name': 'Slovenian'},
        {'code': 'es', 'flag': '🇪🇸', 'name': 'Spanish'},
        {'code': 'sw', 'flag': '🇰🇪', 'name': 'Swahili'},
        {'code': 'sv', 'flag': '🇸🇪', 'name': 'Swedish'},
        {'code': 'tl', 'flag': '🇵🇭', 'name': 'Tagalog'},
        {'code': 'ta', 'flag': '🇮🇳', 'name': 'Tamil'},
        {'code': 'th', 'flag': '🇹🇭', 'name': 'Thai'},
        {'code': 'tr', 'flag': '🇹🇷', 'name': 'Turkish'},
        {'code': 'uk', 'flag': '🇺🇦', 'name': 'Ukrainian'},
        {'code': 'ur', 'flag': '🇵🇰', 'name': 'Urdu'},
        {'code': 'vi', 'flag': '🇻🇳', 'name': 'Vietnamese'},
        {'code': 'cy', 'flag': '🏴', 'name': 'Welsh'},
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

@translator_router.callback_query(lambda callback_query: callback_query.data.startswith('page:'))
async def process_page_navigation(callback_query: types.CallbackQuery):
    # Извлекаем номер страницы из callback_data
    page = int(callback_query.data.split(':')[1])

    # Создаем обновленную клавиатуру с выбранной страницей
    keyboard = keyboards.CustomKeyboard.inline_translated_languages_for_translator(page=page)

    # Обновляем сообщение с новой клавиатурой
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)

    # Отвечаем на callback, чтобы убрать индикатор загрузки
    await callback_query.answer()



@translator_router.callback_query(lambda callback_query: callback_query.data.startswith('translator_dest_lang:'))
async def process_overlap_value_button(callback_query: types.CallbackQuery):
    db.connect()
    dest = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_user_settings('translator_id_panel', user_id)
    db.update_user_settings(key='dest_lang', value=dest, user_id=user_id)
    languages = [
        {'code': 'af', 'flag': '🇿🇦', 'name': 'Afrikaans'},
        {'code': 'ar', 'flag': '🇸🇦', 'name': 'Arabic'},
        {'code': 'hy', 'flag': '🇦🇲', 'name': 'Armenian'},
        {'code': 'az', 'flag': '🇦🇿', 'name': 'Azerbaijani'},
        {'code': 'be', 'flag': '🇧🇾', 'name': 'Belarusian'},
        {'code': 'bs', 'flag': '🇧🇦', 'name': 'Bosnian'},
        {'code': 'bg', 'flag': '🇧🇬', 'name': 'Bulgarian'},
        {'code': 'ca', 'flag': '🇪🇸', 'name': 'Catalan'},
        {'code': 'zh-cn', 'flag': '🇨🇳', 'name': 'Chinese (Simplified)'},
        {'code': 'hr', 'flag': '🇭🇷', 'name': 'Croatian'},
        {'code': 'cs', 'flag': '🇨🇿', 'name': 'Czech'},
        {'code': 'da', 'flag': '🇩🇰', 'name': 'Danish'},
        {'code': 'nl', 'flag': '🇳🇱', 'name': 'Dutch'},
        {'code': 'en', 'flag': '🇬🇧', 'name': 'English'},
        {'code': 'et', 'flag': '🇪🇪', 'name': 'Estonian'},
        {'code': 'fi', 'flag': '🇫🇮', 'name': 'Finnish'},
        {'code': 'fr', 'flag': '🇫🇷', 'name': 'French'},
        {'code': 'gl', 'flag': '🇪🇸', 'name': 'Galician'},
        {'code': 'de', 'flag': '🇩🇪', 'name': 'German'},
        {'code': 'el', 'flag': '🇬🇷', 'name': 'Greek'},
        {'code': 'he', 'flag': '🇮🇱', 'name': 'Hebrew'},
        {'code': 'hi', 'flag': '🇮🇳', 'name': 'Hindi'},
        {'code': 'hu', 'flag': '🇭🇺', 'name': 'Hungarian'},
        {'code': 'is', 'flag': '🇮🇸', 'name': 'Icelandic'},
        {'code': 'id', 'flag': '🇮🇩', 'name': 'Indonesian'},
        {'code': 'it', 'flag': '🇮🇹', 'name': 'Italian'},
        {'code': 'ja', 'flag': '🇯🇵', 'name': 'Japanese'},
        {'code': 'kn', 'flag': '🇮🇳', 'name': 'Kannada'},
        {'code': 'kk', 'flag': '🇰🇿', 'name': 'Kazakh'},
        {'code': 'ko', 'flag': '🇰🇷', 'name': 'Korean'},
        {'code': 'lv', 'flag': '🇱🇻', 'name': 'Latvian'},
        {'code': 'lt', 'flag': '🇱🇹', 'name': 'Lithuanian'},
        {'code': 'mk', 'flag': '🇲🇰', 'name': 'Macedonian'},
        {'code': 'ms', 'flag': '🇲🇾', 'name': 'Malay'},
        {'code': 'mr', 'flag': '🇮🇳', 'name': 'Marathi'},
        {'code': 'mi', 'flag': '🇳🇿', 'name': 'Maori'},
        {'code': 'ne', 'flag': '🇳🇵', 'name': 'Nepali'},
        {'code': 'no', 'flag': '🇳🇴', 'name': 'Norwegian'},
        {'code': 'fa', 'flag': '🇮🇷', 'name': 'Persian'},
        {'code': 'pl', 'flag': '🇵🇱', 'name': 'Polish'},
        {'code': 'pt', 'flag': '🇵🇹', 'name': 'Portuguese'},
        {'code': 'ro', 'flag': '🇷🇴', 'name': 'Romanian'},
        {'code': 'ru', 'flag': '🇷🇺', 'name': 'Russian'},
        {'code': 'sr', 'flag': '🇷🇸', 'name': 'Serbian'},
        {'code': 'sk', 'flag': '🇸🇰', 'name': 'Slovak'},
        {'code': 'sl', 'flag': '🇸🇮', 'name': 'Slovenian'},
        {'code': 'es', 'flag': '🇪🇸', 'name': 'Spanish'},
        {'code': 'sw', 'flag': '🇰🇪', 'name': 'Swahili'},
        {'code': 'sv', 'flag': '🇸🇪', 'name': 'Swedish'},
        {'code': 'tl', 'flag': '🇵🇭', 'name': 'Tagalog'},
        {'code': 'ta', 'flag': '🇮🇳', 'name': 'Tamil'},
        {'code': 'th', 'flag': '🇹🇭', 'name': 'Thai'},
        {'code': 'tr', 'flag': '🇹🇷', 'name': 'Turkish'},
        {'code': 'uk', 'flag': '🇺🇦', 'name': 'Ukrainian'},
        {'code': 'ur', 'flag': '🇵🇰', 'name': 'Urdu'},
        {'code': 'vi', 'flag': '🇻🇳', 'name': 'Vietnamese'},
        {'code': 'cy', 'flag': '🏴', 'name': 'Welsh'},
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
