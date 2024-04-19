from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingStateGpt
from spawnbot import bot
from menu import keyboards, texts

gpt_settings = Router()


@gpt_settings.callback_query(F.data == '⚙️ Настройки')
async def change_gpt_settings(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    await state.set_state(WaitingStateGpt.settings)
    markup = keyboards.CustomKeyboard.create_inline_kb_default_settings().as_markup()
    await bot.send_message(user_id, '<b>Введите настройки</b>', reply_markup=markup)


@gpt_settings.message(WaitingStateGpt.settings)
async def process_settings(message: Message, state: FSMContext) -> None:
    user_id, settings = message.from_user.id, message.text
    db.connect()
    db.add_settings(user_id=user_id, settings=settings)
    db.disconnect()
    await message.answer(f'<b>Ваши настройки сохранены:</b>\n<i>{settings}</i>')
    await state.clear()



@gpt_settings.callback_query(F.data == '🌡 Градус')
async def change_gpt_degree(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    await state.set_state(WaitingStateGpt.degree)
    await bot.send_message(user_id, '<b>Введите темперауру ответов от ChatGpt</b>')


@gpt_settings.message(WaitingStateGpt.degree)
async def process_degree(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    try:
        degree = float(message.text)

        if not(0<=degree and degree<=1):
            raise ValueError
        db.connect()
        db.add_degree(user_id, degree)
        db.disconnect()
        await bot.send_message(user_id, '<b>Температура записана</b>')
        await state.clear()
    except ValueError:
        await bot.send_message(user_id, '❌ Введите число в диапазоне [0:1.0]')