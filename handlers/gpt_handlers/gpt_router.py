from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from menu import keyboards, texts
from menu.keyboards import ChatGpt

gpt_router = Router()


@gpt_router.message(F.text == '🤖 ChatGpt')
async def create_gpt_request_for_request(message: Message):
    f_text = "🤖 ChatGpt"
    user_id = message.from_user.id
    setting = await db.get_user_setting('gpt', user_id)
    degree = await db.get_user_setting('degree', user_id)
    model = await db.get_user_setting('gpt_model', user_id)
    tokens = await db.get_user_setting('gpt_tokens', user_id)

    markup_reply = keyboards.CustomKeyboard.create_gpt_buttons()
    process_bool = await db.get_user_setting('postprocess_bool', user_id)
    inline_reply = ChatGpt.create_gpt_settings(process_bool)

    need_analysis = await db.get_user_setting('postprocess_bool', user_id)
    similarity_threshold = await db.get_user_setting('similarity_threshold', user_id)

    frequency_penalty_gpt = await db.get_user_setting('frequency_penalty_gpt', user_id)
    reasoning_effort_gpt = await db.get_user_setting('reasoning_effort_gpt', user_id)
    presence_penalty_gpt = await db.get_user_setting('presence_penalty_gpt', user_id)

    new_text_to_panel = texts.settings_request_with_postprocessing.format(setting,
                                                                          degree,
                                                                          model,
                                                                          tokens,
                                                                          similarity_threshold,
                                                                          frequency_penalty_gpt,
                                                                          reasoning_effort_gpt,
                                                                          presence_penalty_gpt)

    await message.answer(f'{texts.future_request_information.format(f_text)}', reply_markup=markup_reply)
    id_gpt_panel = await message.answer(new_text_to_panel,
                                        reply_markup=inline_reply)

    id_gpt_panel = id_gpt_panel.message_id
    await db.update_user_setting('id_gpt_panel', id_gpt_panel, user_id)


@gpt_router.message(F.text == '◀️ Назад')
async def go_to_main_menu(message: Message, state: FSMContext):
    markup = keyboards.CustomKeyboard.create_reply_main_menu()
    await message.answer('<b>Главное меню</b>', reply_markup=markup)
    await state.clear()
