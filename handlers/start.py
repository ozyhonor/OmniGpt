from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from db.database import db
from menu.keyboards import CustomKeyboard
from menu.texts import video_settings_message
import asyncio




start_router = Router()


def restricted(func):
    @wraps(func)
    async def wrapped(message: types.Message, *args, **kwargs):
        if message.from_user.id not in ALLOWED_USERS:
            await message.reply("У вас нет доступа к этой команде.")
            return
        return await func(message, *args, **kwargs)
    return wrapped

@start_router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    markup = CustomKeyboard.create_reply_main_menu()
    markup_accept = CustomKeyboard.create_pls_accept()
    user_name = message.from_user.full_name
    user_id = message.from_user.id
    is_user_exist_value = await db.is_user_exist(user_id)
    if is_user_exist_value:
        await message.answer(f"Привет, <b>{user_name}!</b>", reply_markup=markup)
    else:
        await message.answer(f"Привет, <b>{user_name}</b> !, получите доступ", reply_markup=markup_accept)
