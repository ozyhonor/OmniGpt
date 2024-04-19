from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from db.database import db
from menu.keyboards import CustomKeyboard

start_router = Router()


@start_router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    print(message.from_user.id)
    markup = CustomKeyboard.create_reply_main_menu()
    markup_accept = CustomKeyboard.create_pls_accept()
    user_id = message.from_user.id
    db.connect()
    if not db.is_user_exist(user_id):
        await message.answer(f"Привет, <b>{message.from_user.full_name}</b> !, получите доступ", reply_markup=markup_accept)
    else:
        await message.answer(f"Привет, <b>{message.from_user.full_name}!</b>", reply_markup=markup)
    db.disconnect()


