from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from menu import keyboards, texts

video_router = Router()


@video_router.message(F.text == '🎥 Видео')
async def create_youtube_subtitles(message: Message):
    user_id = message.from_user.id


    buttons1 = keyboards.CustomKeyboard.create_inline_video_settings_buttons()
    buttons2 = keyboards.CustomKeyboard.create_video_main()
    await message.answer(f'{texts.future_request_information}', reply_markup=buttons2)
    await message.answer(f'{texts.video_settings_message}', reply_markup=buttons1)