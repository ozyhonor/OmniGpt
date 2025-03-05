from aiogram import Router, F
from aiogram.types import Message
import states.states
import re
from utils.remove_similar_sentences import remove_similar_sentences
from utils.decode_any_format import TYPE_TXT_FILE
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states.states import WaitingStateGpt
from spawnbot import bot
from menu import keyboards, texts
from db.database import db
import os
from utils.sort_file import sort_and_filter
from utils.decode_any_format import detect_file_format
from utils.gpt_requests import chunks_request
from utils.split_text_for_gpt import split_text


gpt_file = Router()



@gpt_file.message(F.text == '🗂 Файл')
async def process_message_gpt_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    if not(await db.is_user_exist(user_id)): return
    await state.set_state(WaitingStateGpt.file_gpt)
    await bot.send_message(user_id, '<b>Ожидается файловый запрос</b>')


def get_first_score(text):
    # Поиск первого числа (может быть с плавающей точкой)
    match = re.search(r"\d+(\.\d+)?", text)
    # Если число найдено, вернем его как float, иначе 0
    return float(match.group()) if match else 0

def safe_remove(file_path):
    """Удаляет файл, если он существует."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Файл {file_path} удалён.")
        else:
            print(f"Файл {file_path} не существует.")
    except Exception as e:
        print(f"Не удалось удалить файл {file_path}: {e}")


@gpt_file.message(WaitingStateGpt.file_gpt)
async def process_file_gpt_request(message: Message, state: FSMContext, settings=None) -> None:
    states.states.stop_gpt = False
    markup = keyboards.CustomKeyboard.create_stop_button().as_markup()
    user_id = message.from_user.id
    result: bool = await bot.send_chat_action(user_id, 'upload_document')
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    postprocess_bool = await db.get_user_setting('postprocess_bool', user_id)
    file_path = file.file_path
    main_file_name = ['txt files/', message.document.file_name]
    await bot.download_file(file_path, main_file_name[0]+main_file_name[1])
    similar_sentences_files = ['', '', '']
    text = detect_file_format(main_file_name[0]+main_file_name[1])
    model = await db.get_user_setting('gpt_model', user_id)
    marks = await db.get_user_setting('gpt_tokens', user_id)
    similar = await db.get_user_setting('similarity_threshold', user_id)
    result: bool = await bot.send_chat_action(user_id, 'typing')
    try:
        marks = int(marks)
        symbol = None
    except:
        symbol = marks
    chunks = split_text(text, token=marks, symbol=symbol)
    await message.answer(f'<b>Количество запросов в файле</b>: {len(chunks)}\n', reply_markup=markup)

    answer = await chunks_request(chunks, message, settings)

    await message.answer(texts.water_mark_omnigpt.format(answer[2]))


    file_name = main_file_name[1].rsplit('.', 1)[0] + '.txt'

    with open(file_name, "w", encoding=TYPE_TXT_FILE or "utf-8") as file:
        for answer in answer[1]:
            file.write(str(answer) + "\n\n")
    document = FSInputFile("txt files/GPT"+file_name)
    await bot.send_document(message.chat.id, document)

    if postprocess_bool:

        similar_sentences_files = await remove_similar_sentences("txt files/GPT"+file_name, similar)
        document_deleted = FSInputFile(similar_sentences_files[0])
        await bot.send_message(message.chat.id, 'фильтрованный файл')
        await bot.send_document(message.chat.id, document_deleted)

        document_filtered = FSInputFile(similar_sentences_files[1])
        await bot.send_message(message.chat.id, 'предложения, которые были удалены')
        await bot.send_document(message.chat.id, document_filtered)

        document_paired = FSInputFile(similar_sentences_files[2])
        await bot.send_message(message.chat.id, 'похожие предложения')
        await bot.send_document(message.chat.id, document_paired)

    files_to_remove = [
        f"txt files/{file_name}",
        f'{file_name}',
        similar_sentences_files[0],
        similar_sentences_files[1],
        similar_sentences_files[2],
        f'txt files/sorted{file_name}',
        f'txt files/GPT{file_name}',
        f'{main_file_name[0] + main_file_name[1]}'
    ]

    # Пробуем удалить каждый файл
    for file_path in files_to_remove:
        safe_remove(file_path)

    await state.clear()

@gpt_file.callback_query(lambda callback_query: callback_query.data == 'stop_gpt')
async def stop_gpt_handler(callback_query: types.CallbackQuery):
    states.states.stop_gpt = True
    await callback_query.answer("Остановка GPT")
