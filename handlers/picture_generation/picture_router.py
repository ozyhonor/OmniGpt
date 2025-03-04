from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from menu import keyboards, texts

picture_router = Router()


@picture_router.message(F.text == '👨‍🎨 Визуализация')
async def create_gpt_request_for_request(message: Message):
    user_id = message.from_user.id

    prompt = await db.get_user_setting('picture_prompt', user_id)
    model = await db.get_user_setting('picture_model', user_id)
    size = await db.get_user_setting('picture_size', user_id)
    picture_count = await db.get_user_setting('picture_count', user_id)

    markup = keyboards.CustomKeyboard.create_picture_buttons()
    f_text = '👨‍🎨 Визуализация'
    markup_inline = keyboards.CustomKeyboard.create_inline_picture_settings()
    await message.answer(f'{texts.future_request_information.format(f_text)}', reply_markup=markup)
    text = texts.picture_panel.format(prompt, model, size, picture_count)

    id_picture_panel = await message.answer(text, reply_markup=markup_inline)
    id_picture_panel = id_picture_panel.message_id
    await db.update_user_setting('id_picture_panel', id_picture_panel, user_id)





