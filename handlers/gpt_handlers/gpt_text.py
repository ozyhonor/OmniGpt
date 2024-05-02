from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingStateGpt
from spawnbot import bot
from menu import texts

from utils.gpt_requests import solo_request


gpt_text = Router()

@gpt_text.message(F.text == '🗒 Текст')
async def process_message_gpt_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(WaitingStateGpt.text_gpt)
    user_id = message.from_user.id
    await bot.send_message(user_id, '<b>Ожидается текстовый запрос</b>')


@gpt_text.message(WaitingStateGpt.text_gpt)
async def go_gpt_text_request(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    db.connect()
    answer = solo_request(None, message, db.get_degree(user_id), None, None)
    db.disconnect()
    print(answer[1])
    await message.answer(texts.water_mark_omnigpt.format(answer[0]))
    await message.answer(f'{str(answer[1])}', parse_mode='Markdown')
    await state.clear()
