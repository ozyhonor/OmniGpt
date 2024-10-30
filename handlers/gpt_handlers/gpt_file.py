from aiogram import Router, F
from aiogram.types import Message
import states.states
import re
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


@gpt_file.message(WaitingStateGpt.file_gpt)
async def process_file_gpt_request(message: Message, state: FSMContext, settings=None) -> None:
    states.states.stop_gpt = False
    markup = keyboards.CustomKeyboard.create_stop_button().as_markup()
    user_id = message.from_user.id
    result: bool = await bot.send_chat_action(user_id, 'upload_document')
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    postprocess_bool = await db.get_user_setting('postprocess_bool', user_id)
    print(file)
    file_path = file.file_path
    main_file_name = ['txt files/', message.document.file_name]
    await bot.download_file(file_path, main_file_name[0]+main_file_name[1])

    text = detect_file_format(main_file_name[0]+main_file_name[1])
    model = await db.get_user_setting('gpt_model', user_id)
    result: bool = await bot.send_chat_action(user_id, 'typing')
    chunks = split_text(text, model=model)
    await message.answer(f'<b>Количество запросов в файле</b>: {len(chunks)}\n', reply_markup=markup)

    answer = await chunks_request(chunks, message, settings)

    await message.answer(texts.water_mark_omnigpt.format(answer[2]))


    file_name = main_file_name[1].rsplit('.', 1)[0] + '.txt'
    document = FSInputFile("txt files/GPT"+file_name)
    await bot.send_document(message.chat.id, document)

    print(postprocess_bool)
    if postprocess_bool:
        sorted_texts = sorted(answer[1], key=get_first_score, reverse=True)
        file_name = f"txt files/sortedGPT"+file_name
        with open(file_name, "w", encoding=TYPE_TXT_FILE or "utf-8") as file:
            for answer in sorted_texts or 'omni':
                file.write(answer + "\n\n")

        document2 = FSInputFile(file_name)
        await bot.send_document(message.chat.id, document2)

    os.remove("txt files/sorted GPT" + file_name)
    os.remove(f'txt files/GPT{file_name}')
    os.remove(f'{main_file_name[0]+main_file_name[1]}')

    await state.clear()

@gpt_file.callback_query(lambda callback_query: callback_query.data == 'stop_gpt')
async def stop_gpt_handler(callback_query: types.CallbackQuery):
    states.states.stop_gpt = True
    await callback_query.answer("Остановка GPT")
