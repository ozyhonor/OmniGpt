from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from menu import keyboards, texts

speech_router = Router()


@speech_router.message(F.text == '🎙 Озвучка')
async def create_gpt_request_for_request(message: Message):
    user_id = message.from_user.id
    f_text = '🎙 Озвучка'
    voice = await db.get_user_setting('synthes_voice', user_id)
    rate = await db.get_user_setting('synthes_speed', user_id)


    buttons1 = keyboards.CustomKeyboard.create_speech_main()
    await message.answer(f'{texts.future_request_information.format(f_text)}', reply_markup=buttons1)

    buttons2 = keyboards.CustomKeyboard.create_inline_speech_settings().as_markup()
    panel_id = await message.answer(f'{texts.synthesis_information.format(rate, voice)}', reply_markup=buttons2)
    panel_id = panel_id.message_id
    await db.update_user_setting('id_speech_panel', panel_id, user_id)




