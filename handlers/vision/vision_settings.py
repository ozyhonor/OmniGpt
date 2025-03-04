from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingStateVision
from spawnbot import bot
from aiogram import types
from menu import keyboards, texts

vision_settings_router = Router()

@vision_settings_router.callback_query(lambda callback_query: callback_query.data == 'vision_prompt')
async def change_vision_prompt(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await db.get_user_setting('vision_prompt', user_id)
    await state.set_state(WaitingStateVision.vision_settings)
    markup = keyboards.ChatGpt.create_inline_kb_default_settings()
    await bot.send_message(user_id, texts.write_gpt_settings, reply_markup=markup)
    await db.get_user_setting('vision_model', user_id)


@vision_settings_router.message(WaitingStateVision.vision_settings)
async def process_settings(message: Message, state: FSMContext) -> None:
    user_id, settings = message.from_user.id, message.text

    panel_id = await db.get_user_setting('id_vision_panel', user_id)
    markup = keyboards.CustomKeyboard.create_vision_button()
    await db.update_user_setting('vision_prompt', settings, user_id)
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    new_text_settings = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    await state.clear()


@vision_settings_router.callback_query(lambda callback_query: callback_query.data == 'vision_prompt')
async def change_vision_prompt(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await db.get_user_setting('vision_prompt', user_id)
    await state.set_state(WaitingStateVision.vision_settings)
    markup = keyboards.ChatGpt.create_inline_kb_default_settings()
    await bot.send_message(user_id, texts.write_gpt_settings, reply_markup=markup)
    await db.get_user_setting('vision_model', user_id)

@vision_settings_router.callback_query(lambda callback_query: callback_query.data == 'vision_model')
async def change_vision_model(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    markup = keyboards.CustomKeyboard.create_vision_models()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=markup)

@vision_settings_router.message(WaitingStateVision.vision_model)
async def process_settings(message: Message, state: FSMContext) -> None:
    user_id, settings = message.from_user.id, message.text

    panel_id = await db.get_user_setting('id_vision_panel', user_id)
    markup = keyboards.CustomKeyboard.create_vision_button()
    await db.update_user_setting('vision_model', settings, user_id)
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    new_text_settings = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    await state.clear()

@vision_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('vision_model:'))
async def change_gpt_model(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    model = callback_query.data.split(':')[1]
    panel_id = await db.get_user_setting('id_vision_panel', user_id)
    message_id = callback_query.message.message_id
    await db.update_user_setting('vision_model', model, user_id)

    markup = keyboards.CustomKeyboard.create_vision_button()
    new_text_settings = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


async def reload_settings(user_id):

    prompt = await db.get_user_setting('vision_prompt', user_id)
    model = await db.get_user_setting('vision_model', user_id)
    text = texts.vision_request.format(prompt, model)
    return text
