from aiogram import Router, F
from aiogram.types import Message
import states.states
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states.states import WaitingStateGpt
from spawnbot import bot
from menu import keyboards, texts
import os
from utils.sort_file import sort_and_filter
from utils.decode_any_format import detect_file_format
from utils.gpt_requests import file_request
from utils.split_text_for_gpt import split_text


gpt_file = Router()



@gpt_file.message(F.text == '🗂 Файл')
async def process_message_gpt_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    await state.set_state(WaitingStateGpt.file_gpt)
    await bot.send_message(user_id, '<b>Ожидается файловый запрос</b>')


@gpt_file.message(WaitingStateGpt.file_gpt)
async def process_file_gpt_request(message: Message, state: FSMContext, settings=None) -> None:
    """

    """
    states.states.stop_gpt = False
    markup = keyboards.CustomKeyboard.create_stop_button().as_markup()
    result: bool = await bot.send_chat_action(message.from_user.id, 'upload_document')
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    print(file)
    file_path = file.file_path
    main_file_name = ['txt files/', message.document.file_name]
    await bot.download_file(file_path, main_file_name[0]+main_file_name[1])

    text = detect_file_format(main_file_name[0]+main_file_name[1])

    chunks = split_text(text)

    await message.answer(f'<b>Количество запросов в файле</b>: {len(chunks)}\n', reply_markup=markup)

    answer = await file_request(chunks, message, settings)

    await message.answer(texts.water_mark_omnigpt.format(answer[0]))

    file_name = main_file_name[1].rsplit('.', 1)[0] + '.txt'
    document = FSInputFile("txt files/GPT"+file_name)
    await bot.send_document(message.chat.id, document)

    sort_and_filter("GPT"+file_name)
    document = FSInputFile("txt files/sorted GPT" + file_name)
    await bot.send_document(message.chat.id, document)

    os.remove("txt files/sorted GPT" + file_name)
    os.remove(f'txt files/GPT{file_name}')
    os.remove(f'{main_file_name[0]+main_file_name[1]}')

    await state.clear()

@gpt_file.callback_query(lambda callback_query: callback_query.data == 'stop_gpt')
async def stop_gpt_handler(callback_query: types.CallbackQuery):
    states.states.stop_gpt = True
    await callback_query.answer("Остановка GPT")
