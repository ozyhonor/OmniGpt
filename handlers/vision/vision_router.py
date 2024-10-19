from aiogram import Router, F
from aiogram.types import Message
from utils.edit_content.create_translate import create_translate_text
from db.database import db
from aiogram import Router, F
from menu.texts import languages
from aiogram.types import Message
import states.states
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states.states import WaitingStateGpt
from aiogram.fsm.context import FSMContext
from menu import keyboards, texts
from spawnbot import bot
from aiogram import types
from spawnbot import bot
from aiogram import Router
from  db.database import db
from aiogram.types import Message
from states.states import WaitingStateVision
from aiogram.fsm.context import FSMContext
from menu import texts
import os
from aiogram import types
from utils.decode_any_format import detect_file_format
from utils.split_text_for_gpt import (split_text)


vision_router = Router()


@vision_router.message(F.text == '👁‍🗨 Зрение')
async def create_gpt_request_for_request(message: Message):
    user_id = message.from_user.id
    vision_prompt = await db.get_user_setting('vision_prompt', user_id)
    vision_model = await db.get_user_setting('vision_model', user_id)
    markup_inline = keyboards.CustomKeyboard.create_vision_button()
    markup_reply = keyboards.CustomKeyboard.create_vision_buttons_down()

    await message.answer(f'{texts.future_request_information.format('👁‍🗨 Зрение')}', reply_markup=markup_reply)
    text = texts.vision_request.format(vision_prompt, vision_model)
    id_vision_panel = await message.answer(text, reply_markup=markup_inline)
    id_vision_panel = id_vision_panel.message_id
    await db.update_user_setting('id_vision_panel', id_vision_panel, user_id)

