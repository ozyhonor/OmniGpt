from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingStateGpt
from spawnbot import bot
from menu import keyboards, texts

picture_settings = Router()


@picture_settings.callback_query(lambda callback_query: callback_query.data =='model_picture')
async def change_model_picture(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    id_panel = await db.get_user_setting('id_picture_panel', user_id)
    markup = keyboards.CustomKeyboard.create_inline_picture_models()
    await bot.edit_message_reply_markup(user_id, id_panel, texts.write_gpt_settings, reply_markup=markup)


@picture_settings.callback_query(lambda callback_query: callback_query.data.startswith('model_picture:'))
async def change_model_picture(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_picture_panel', user_id)
    model = callback_query.data.split(':')[1]
    await db.update_user_setting('picture_model', model, user_id)

    markup = keyboards.CustomKeyboard.create_inline_picture_settings()
    new_text_settings = await reload_settings(user_id)

    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@picture_settings.callback_query(lambda callback_query: callback_query.data =='size_picture')
async def change_size_picture(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    id_panel = await db.get_user_setting('id_picture_panel', user_id)
    markup = keyboards.CustomKeyboard.create_picture_size_menu()
    await bot.edit_message_reply_markup(user_id, id_panel, texts.write_gpt_settings, reply_markup=markup)


@picture_settings.callback_query(lambda callback_query: callback_query.data.startswith('picture_size:'))
async def do_size_picture(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_picture_panel', user_id)
    size = callback_query.data.split(':')[1]
    await db.update_user_setting('picture_size', size, user_id)

    markup = keyboards.CustomKeyboard.create_inline_picture_settings()
    new_text_settings = await reload_settings(user_id)

    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@picture_settings.callback_query(lambda callback_query: callback_query.data =='count_picture')
async def change_count_picture(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    id_panel = await db.get_user_setting('id_picture_panel', user_id)
    markup = keyboards.CustomKeyboard.create_picture_count_menu()
    await bot.edit_message_reply_markup(user_id, id_panel, texts.write_gpt_settings, reply_markup=markup)


@picture_settings.callback_query(lambda callback_query: callback_query.data.startswith('picture_count:'))
async def do_change_count_picture(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_picture_panel', user_id)
    count = callback_query.data.split(':')[1]
    await db.update_user_setting('picture_count', count, user_id)

    markup = keyboards.CustomKeyboard.create_inline_picture_settings()
    new_text_settings = await reload_settings(user_id)

    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@picture_settings.callback_query(lambda callback_query: callback_query.data =='picture_back')
async def picture_back(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    id_panel = await db.get_user_setting('id_picture_panel', user_id)
    markup = keyboards.CustomKeyboard.create_picture_buttons()
    await bot.edit_message_reply_markup(user_id, id_panel, texts.write_gpt_settings, reply_markup=markup)



async def reload_settings(user_id):
    picture_settings = await db.get_user_setting('picture_prompt', user_id)
    picture_model = await db.get_user_setting('picture_model', user_id)
    picture_size = await db.get_user_setting('picture_size', user_id)
    count_picture = await db.get_user_setting('picture_count', user_id)

    new_settings = texts.picture_panel.format(picture_settings,
                                                 picture_model,
                                                 picture_size ,
                                                 count_picture)

    return new_settings
