from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingStartSpeech
from spawnbot import bot
from menu import keyboards, texts
from utils.speech_requests import openai_audio_request
from aiogram.types.input_file import FSInputFile


speech_text_router = Router()


@speech_text_router.message(F.text == '✉️ Сообщение')
async def process_message_gpt_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(WaitingStartSpeech.text_speech)
    user_id = message.from_user.id
    await bot.send_message(user_id, '<b>Ожидается текстовый запрос</b>')


@speech_text_router.message(WaitingStartSpeech.text_speech)
async def go_gpt_text_request(message: Message, state: FSMContext) -> None:
    db.connect()
    user_id = message.from_user.id
    user_rate = db.get_rate(user_id)
    user_voice = db.get_voice(user_id)
    db.disconnect()
    outputfilename = 'omnibot'
    result: bool = await bot.send_chat_action(message.from_user.id, 'record_voice')
    answer = openai_audio_request(model="tts-1", voice=user_voice, input_text=message.text, output_file=f"audio_files/{outputfilename}.mp3", speed=user_rate)
    result: bool = await bot.send_chat_action(message.from_user.id, 'upload_voice')
    audio = FSInputFile(f'audio_files/{outputfilename}.mp3')
    await message.answer(texts.water_mark_omnigpt.format(answer[1]))
    await bot.send_audio(message.from_user.id, audio=audio)

    await state.clear()
