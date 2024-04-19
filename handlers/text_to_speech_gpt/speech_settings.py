from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingStartSpeech
from spawnbot import bot
from menu import keyboards, texts

speech_settings_router = Router()


@speech_settings_router.callback_query(F.data == '🔊 Скорость')
async def rate_speech(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    await state.set_state(WaitingStartSpeech.rate)
    await bot.send_message(chat_id=user_id, text=texts.synthesis_rate_info)



@speech_settings_router.message(WaitingStartSpeech.rate)
async def change_rate_speech(message: Message, state: FSMContext):
    db.connect()
    try:
        db.add_rate(message.from_user.id, message.text)
        await message.answer(f'<b>Скорость изменена</b>')
    except Exception as e:
        print(e)
    await state.clear()
    db.disconnect()


@speech_settings_router.callback_query(F.data == '🗣 Голос')
async def voice_speech(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    await state.set_state(WaitingStartSpeech.voice)
    await bot.send_message(chat_id=user_id, text=texts.synthesis_voice_info)



@speech_settings_router.message(WaitingStartSpeech.voice)
async def change_voice_speech(message: Message, state: FSMContext):
    db.connect()
    try:
        db.add_voice(message.from_user.id, message.text)
        await message.answer(f'<b>Голос изменен</b>')
    except Exception as e:
        print(e)
    await state.clear()
    db.disconnect()

