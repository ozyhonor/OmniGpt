from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from menu import keyboards, texts

youtube_router = Router()


@youtube_router.message(F.text == '🚩 Ютуб')
async def create_youtube_subtitles(message: Message):
    user_id = message.from_user.id

    voice = db.get_voice(user_id)
    rate = db.get_rate(user_id)

    buttons1 = keyboards.CustomKeyboard.create_youtube_buttons()
    await message.answer(f'{texts.future_request_information}', reply_markup=buttons1)
