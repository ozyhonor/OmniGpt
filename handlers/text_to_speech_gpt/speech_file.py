from aiogram import Router, F
from aiogram.types import Message
import states.states
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states.states import WaitingStartSpeech
from spawnbot import bot
from menu import keyboards, texts
import os
from utils.sort_file import sort_and_filter
from utils.decode_any_format import detect_file_format
import shutil
from utils.split_text_for_gpt import split_text
from utils.speech_requests import file_request
from utils.create_download_link import upload_to_gofileio


speech_file_router = Router()


@speech_file_router.message(F.text == '📁 Файл')
async def process_message_gpt_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    await state.set_state(WaitingStartSpeech.file_speech)
    await bot.send_message(user_id, '<b>Ожидается файловый запрос</b>')


@speech_file_router.message(WaitingStartSpeech.file_speech)
async def process_file_gpt_request(message: Message, state: FSMContext) -> None:
    markup = keyboards.CustomKeyboard.create_stop_button().as_markup()
    result: bool = await bot.send_chat_action(message.from_user.id, 'upload_document')
    file_id = message.document.file_id
    file = await bot.get_file(file_id)

    file_path = file.file_path
    main_file_name = ['txt files/', message.document.file_name]
    await bot.download_file(file_path, main_file_name[0]+main_file_name[1])

    text = detect_file_format(main_file_name[0]+main_file_name[1])
    print(text)
    chunks = split_text(text, 3500)
    await message.answer(f'<b>Количество запросов в файле</b>: {len(chunks)}\n', reply_markup=markup)

    answer = await file_request(chunks, message)

    result: bool = await bot.send_chat_action(message.from_user.id, 'upload_voice')

    file_size_bytes = os.path.getsize('audio_files/output.mp3')

    file_size_mb = file_size_bytes / (1024 ** 2)
    if file_size_mb > 47:
        link = await upload_to_gofileio('audio_files/output.mp3')
        await message.answer(f'Ваша ссылка на файл: {link}')
        shutil.rmtree('audio_files')
        os.makedirs('audio_files')
    else:
        audio = FSInputFile(f'audio_files/output.mp3')
        await message.answer(texts.water_mark_omnigpt.format(answer[1]))

        await bot.send_audio(message.from_user.id, audio=audio)
        shutil.rmtree('audio_files')
        os.makedirs('audio_files')

    await state.clear()
