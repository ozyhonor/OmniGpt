from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from menu import keyboards, texts

speech_router = Router()


@speech_router.message(F.text == '🎧 Озвучка')
async def create_gpt_request_for_request(message: Message):
    user_id = message.from_user.id
    db.connect()
    voice = db.get_voice(user_id)
    rate = db.get_rate(user_id)
    db.disconnect()

    buttons1 = keyboards.CustomKeyboard.create_speech_main()
    await message.answer(f'{texts.future_request_information}', reply_markup=buttons1)

    buttons2 = keyboards.CustomKeyboard.create_inline_speech_settings().as_markup()
    await message.answer(f'{texts.synthesis_information.format(rate, voice)}', reply_markup=buttons2)



