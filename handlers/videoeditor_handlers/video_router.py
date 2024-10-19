from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from menu import keyboards, texts
from handlers.videoeditor_handlers.video_settings_router import reload_settings

video_router = Router()


@video_router.message(F.text == '🎥 Видео')
async def create_youtube_subtitles(message: Message):
    user_id = message.from_user.id

    dict_bool = {1 : '✅', 0 : '❌'}

    buttons1 = keyboards.CustomKeyboard.create_inline_video_settings_buttons()
    buttons2 = keyboards.CustomKeyboard.create_video_main()
    await message.answer(f'{texts.future_request_information.format('🎥 Видео')}', reply_markup=buttons2)
    settings = await reload_settings(user_id)
    id_panel = await message.answer(settings, reply_markup=buttons1)
    print(id_panel)
    panel_message_id = id_panel.message_id

    await db.update_user_setting('id_settings_panel', panel_message_id, user_id)