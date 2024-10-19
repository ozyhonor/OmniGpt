from aiogram import Router, F
from aiogram.types import Message
from utils.edit_content.create_translate import create_translate_text
from db.database import db
from aiogram import Router, F
from menu.texts import languages
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
from utils.decode_any_format import detect_file_format
from utils.split_text_for_gpt import split_text


translator_router = Router()


async def get_dest_and_flag(user_id):
    dest_lang = await db.get_user_setting('dest_lang', user_id)
    flag = 0
    for language in languages:
        if language['code'].lower() == dest_lang.lower():
            flag = language['flag']
    return dest_lang, flag


@translator_router.message(F.text == '🔄 Переводчик')
async def create_gpt_request_for_request(message: Message):
    user_id = message.from_user.id
    f_text = '🔄 Переводчик'

    dest_lang, flag = await get_dest_and_flag(user_id)

    markup_inline = keyboards.CustomKeyboard.inline_translated_languages_for_translator()
    markup_reply = keyboards.CustomKeyboard.create_translator_buttons()

    await message.answer(f'{texts.future_request_information.format(f_text)}', reply_markup=markup_reply)
    text = texts.translator_text_panel.format(dest_lang, flag, '1')
    id_translator_panel = await message.answer(text, reply_markup=markup_inline)
    id_translator_panel = id_translator_panel.message_id
    await db.update_user_setting('translator_id_panel', id_translator_panel, user_id)


@translator_router.callback_query(lambda callback_query: callback_query.data.startswith('page:'))
async def process_page_navigation(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    page = int(callback_query.data.split(':')[1])
    dest_lang, flag = await get_dest_and_flag(user_id)
    text = texts.translator_text_panel.format(dest_lang, flag, f'{page+1}')
    keyboard = keyboards.CustomKeyboard.inline_translated_languages_for_translator(page=page)
    await callback_query.message.edit_text(text=text)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    await callback_query.answer()


@translator_router.callback_query(lambda callback_query: callback_query.data.startswith('translator_dest_lang:'))
async def process_overlap_value_button(callback_query: types.CallbackQuery):
    dest = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('translator_id_panel', user_id)
    await db.update_user_setting(key='dest_lang', value=dest, user_id=user_id)
    dest_lang, flag = await get_dest_and_flag(user_id)
    text = texts.translator_text_panel.format(dest_lang, flag, '1')
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=keyboards.CustomKeyboard.inline_translated_languages_for_translator())


@translator_router.message(F.text == '📧Текст')
async def translate_message_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    await state.set_state(WaitingStateTranslator.text_translate)
    await bot.send_message(user_id, '<b>Ожидается текстовый запрос</b>')


@translator_router.message(F.text == '🗃 Файл')
async def translate_file_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    await state.set_state(WaitingStateTranslator.file_translate)
    await bot.send_message(user_id, '<b>Ожидается файловый запрос</b>')


@translator_router.message(WaitingStateTranslator.text_translate)
async def go_to_translate_message(message: Message, state: FSMContext) -> None:
    result: bool = await bot.send_chat_action(message.from_user.id, 'typing')
    text = message.text
    dest = await db.get_user_setting('dest_lang', message.from_user.id)
    answer = await create_translate_text(text, dest=dest)
    await message.answer(texts.water_mark_omnigpt.format(answer[0]))
    await bot.send_message(message.chat.id, answer)
    await state.clear()



@translator_router.message(WaitingStateTranslator.file_translate)
async def go_translate_request(message: Message, state: FSMContext, settings=None) -> None:
    result: bool = await bot.send_chat_action(message.from_user.id, 'upload_document')
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    main_file_name = ['txt files/', message.document.file_name]
    await bot.download_file(file_path, main_file_name[0]+main_file_name[1])

    text = detect_file_format(main_file_name[0]+main_file_name[1])
    file_name = main_file_name[1].rsplit('.', 1)[0] + '.txt'
    chunks = split_text(text)
    dest = await db.get_user_setting('dest_lang', message.from_user.id)
    new_ = []
    await message.answer(f'<b>Количество запросов в файле</b>: {len(chunks)}\n')
    for _ in chunks:
        a = await create_translate_text(_, dest=dest)
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
    await state.clear()
