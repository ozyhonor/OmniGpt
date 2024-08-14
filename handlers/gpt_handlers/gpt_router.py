from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from menu import keyboards, texts
from spawnbot import bot

gpt_router = Router()


@gpt_router.message(F.text == '🤖 ChatGpt')
async def create_gpt_request_for_request(message: Message):
    db.connect()
    user_id = message.from_user.id
    setting = db.get_settings(user_id)
    degree = db.get_degree(user_id)
    model = db.get_user_settings('gpt_model', user_id)

    markup_inline = keyboards.CustomKeyboard.create_inline_kb_gpt_settings().as_markup()
    markup_reply = keyboards.CustomKeyboard.create_gpt_buttons()

    await message.answer(f'{texts.future_request_information}', reply_markup=markup_reply)

    id_gpt_panel = await message.answer(texts.settings_request.format(setting, degree, model), reply_markup=markup_inline)
    id_gpt_panel = id_gpt_panel.message_id
    db.update_user_settings('id_gpt_panel', id_gpt_panel, user_id)
    db.disconnect()

@gpt_router.message(F.text == '◀️ Назад')
async def go_to_main_menu(message: Message, state: FSMContext):

    markup = keyboards.CustomKeyboard.create_reply_main_menu()
    await message.answer('<b>Главное меню</b>', reply_markup=markup)
    await state.clear()






