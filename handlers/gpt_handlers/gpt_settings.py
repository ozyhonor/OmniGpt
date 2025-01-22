from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingStateGpt
from spawnbot import bot
from menu import keyboards, texts

gpt_settings = Router()


@gpt_settings.callback_query(F.data == '⚙️ Настройки+')
async def change_gpt_postsettings(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    await state.set_state(WaitingStateGpt.postsettings)
    markup = keyboards.ChatGpt.create_inline_kb_default_settings()
    await bot.send_message(user_id, texts.write_gpt_settings, reply_markup=markup)

@gpt_settings.callback_query(F.data == '⚙️ Настройки')
async def change_gpt_settings(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    await state.set_state(WaitingStateGpt.settings)
    markup = keyboards.ChatGpt.create_inline_kb_default_settings()
    await bot.send_message(user_id, texts.write_gpt_settings, reply_markup=markup)


@gpt_settings.callback_query(F.data == '🤖 Модель+')
async def change_gpt_postmodel(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    markup = keyboards.ChatGpt.create_gpt_model_settings('post')
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=markup)



@gpt_settings.callback_query(lambda callback_query: callback_query.data == 'gpt_back_to_main_markup')
async def back_from_model_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    await state.clear()
    process_bool = await db.get_user_setting('postprocess_bool', user_id)
    markup = keyboards.ChatGpt.create_gpt_settings(process_bool)
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=markup)



@gpt_settings.callback_query(F.data == '🤖 Модель')
async def change_gpt_model(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    markup = keyboards.ChatGpt.create_gpt_model_settings()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=markup)


@gpt_settings.callback_query(lambda callback_query: callback_query.data.startswith('postsettings'))
async def change_postprocess_bool(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_gpt_panel', user_id)
    message_id = callback_query.message.message_id
    last_postprocess = await db.get_user_setting('postprocess_bool', user_id)
    await db.update_user_setting('postprocess_bool', not(last_postprocess), user_id)
    process_bool = await db.get_user_setting('postprocess_bool', user_id)
    markup = keyboards.ChatGpt.create_gpt_settings(process_bool)
    new_text_settings = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@gpt_settings.callback_query(lambda callback_query: callback_query.data.startswith('gpt_model:post'))
async def change_gpt_model(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    model = callback_query.data.split(':post')[1]
    panel_id = await db.get_user_setting('id_gpt_panel', user_id)
    message_id = callback_query.message.message_id
    await db.update_user_setting('postmodel', model, user_id)
    process_bool = await db.get_user_setting('postprocess_bool', user_id)
    markup = keyboards.ChatGpt.create_gpt_settings(process_bool)
    new_text_settings = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@gpt_settings.callback_query(lambda callback_query: callback_query.data.startswith('gpt_model:'))
async def change_gpt_model(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    model = callback_query.data.split(':')[1]
    panel_id = await db.get_user_setting('id_gpt_panel', user_id)
    message_id = callback_query.message.message_id
    await db.update_user_setting('gpt_model', model, user_id)
    process_bool = await db.get_user_setting('postprocess_bool', user_id)
    markup = keyboards.ChatGpt.create_gpt_settings(process_bool)
    new_text_settings = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@gpt_settings.message(WaitingStateGpt.postsettings)
async def process_settings(message: Message, state: FSMContext) -> None:
    user_id, settings = message.from_user.id, message.text

    panel_id = await db.get_user_setting('id_gpt_panel', user_id)
    process_bool = await db.get_user_setting('postprocess_bool', user_id)
    markup = keyboards.ChatGpt.create_gpt_settings(process_bool)
    await db.update_user_setting('postprocess_settings', settings, user_id)
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    new_text_settings = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    await state.clear()


@gpt_settings.message(WaitingStateGpt.settings)
async def process_settings(message: Message, state: FSMContext) -> None:
    user_id, settings = message.from_user.id, message.text

    panel_id = await db.get_user_setting('id_gpt_panel', user_id)
    process_bool = await db.get_user_setting('postprocess_bool', user_id)
    markup = keyboards.ChatGpt.create_gpt_settings(process_bool)
    await db.update_user_setting('gpt', settings, user_id)
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    new_text_settings = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    await state.clear()

@gpt_settings.callback_query(F.data == '📏 Разделить')
async def change_gpt_degree(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    markup = keyboards.CustomKeyboard.inline_cancel()
    await state.set_state(WaitingStateGpt.tokens)
    await bot.send_message(user_id, '<b>Введите количество символов в одном запросе ChatGpt до 128 тыс. или разделяющую метку, пример: "#*#*#"</b>', reply_markup=markup)


@gpt_settings.message(WaitingStateGpt.tokens)
async def process_degree(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    panel_id = await db.get_user_setting('id_gpt_panel', user_id)
    process_bool = await db.get_user_setting('postprocess_bool', user_id)
    markup = keyboards.ChatGpt.create_gpt_settings(process_bool)
    try:
        tokens = message.text
        await db.update_user_setting('gpt_tokens', tokens, user_id)
        await message.delete()
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
        new_text_settings = await reload_settings(user_id)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
        await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
        await state.clear()
    except ValueError:
        print('123123')


@gpt_settings.callback_query(F.data == '🌡 Градус')
async def change_gpt_degree(callback_query: CallbackQuery, state: FSMContext) -> None:
    user_id = callback_query.from_user.id
    markup = keyboards.CustomKeyboard.inline_cancel()
    await state.set_state(WaitingStateGpt.degree)
    await bot.send_message(user_id, '<b>Введите темперауру ответов от ChatGpt</b>', reply_markup=markup)


@gpt_settings.message(WaitingStateGpt.degree)
async def process_degree(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    panel_id = await db.get_user_setting('id_gpt_panel', user_id)
    process_bool = await db.get_user_setting('postprocess_bool', user_id)
    markup = keyboards.ChatGpt.create_gpt_settings(process_bool)
    try:
        degree = float(message.text)

        if not(0<=degree and degree<=1):
            raise ValueError
        await db.update_user_setting('degree', degree, user_id)
        await message.delete()
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
        new_text_settings = await reload_settings(user_id)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text_settings)
        await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
        await state.clear()
    except ValueError:
        print('123123')


async def reload_settings(user_id):

    settings = await db.get_user_setting('gpt', user_id)
    degree = await db.get_user_setting('degree', user_id)
    gpt_model = await db.get_user_setting('gpt_model', user_id)
    gpt_tokens = await db.get_user_setting('gpt_tokens', user_id)
    new_settings = texts.settings_request.format(settings,
                                                 degree,
                                                 gpt_model,
                                                 gpt_tokens)
    return new_settings
