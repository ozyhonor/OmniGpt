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
    db.connect()
    user_id = callback_query.from_user.id
    await state.set_state(WaitingStateGpt.settings)
    markup = keyboards.CustomKeyboard.create_inline_kb_default_settings()
    await bot.send_message(user_id, texts.write_gpt_settings, reply_markup=markup)
    db.disconnect()


@gpt_settings.message(WaitingStateGpt.settings)
async def process_settings(message: Message, state: FSMContext) -> None:
    user_id, settings = message.from_user.id, message.text
    db.connect()
    panel_id = db.get_user_settings('id_gpt_panel', user_id)
    markup = keyboards.CustomKeyboard.create_inline_kb_gpt_settings().as_markup()
    db.add_settings(user_id=user_id, settings=settings)
    db.disconnect()
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=reload_settings(user_id))
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    await state.clear()



@gpt_settings.callback_query(F.data == '🌡 Градус')
async def change_gpt_degree(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    markup = keyboards.CustomKeyboard.inline_cancel()
    await state.set_state(WaitingStateGpt.degree)
    await bot.send_message(user_id, '<b>Введите темперауру ответов от ChatGpt</b>', reply_markup=markup)


@gpt_settings.message(WaitingStateGpt.degree)
async def process_degree(message: Message, state: FSMContext) -> None:
    db.connect()
    user_id = message.from_user.id
    panel_id = db.get_user_settings('id_gpt_panel', user_id)
    markup = keyboards.CustomKeyboard.create_inline_kb_gpt_settings().as_markup()
    try:
        degree = float(message.text)

        if not(0<=degree and degree<=1):
            raise ValueError
        db.connect()
        db.add_degree(user_id, degree)
        db.disconnect()
        await message.delete()
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=reload_settings(user_id))
        await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
        await state.clear()
    except ValueError:
        print('123123')
        db.disconnect()
    db.disconnect()

def reload_settings(user_id):
    db.connect()

    new_settings = texts.settings_request.format(db.get_user_settings('gpt', user_id),
                                                 db.get_user_settings('degree', user_id))
    db.disconnect()
    return new_settings