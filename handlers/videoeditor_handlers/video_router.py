from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from menu import keyboards, texts

video_router = Router()


@video_router.message(F.text == '🎥 Видео')
async def create_youtube_subtitles(message: Message):
    db.connect()
    user_id = message.from_user.id

    dict_bool = {1 : '✅', 0 : '❌'}

    buttons1 = keyboards.CustomKeyboard.create_inline_video_settings_buttons()
    buttons2 = keyboards.CustomKeyboard.create_video_main()
    await message.answer(f'{texts.future_request_information}', reply_markup=buttons2)
    id_panel = await message.answer(f'{texts.video_settings_message.format(
        db.get_format(user_id),
        db.get_quality(user_id),
        db.get_resolution(user_id),
        dict_bool[db.get_subtitles(user_id)],
        db.get_font(user_id),
        db.get_size(user_id),
        db.get_color(user_id),
        db.get_position(user_id),
        db.get_outline(user_id),
        db.get_outline_size(user_id),
        db.get_outline_color(user_id),
        db.get_shadow(user_id),
        db.get_shadow_size(user_id),
        db.get_shadow_color(user_id),
        dict_bool[db.get_translator(user_id)],
        db.get_source_language(user_id),
        db.get_translated_language(user_id),
        db.get_original_speed(user_id),
        db.get_translation_speed(user_id),
        db.get_max_words(user_id),
        db.get_smart_sub(user_id),
        db.get_timestamps(user_id)
    )}', reply_markup=buttons1)
    print(id_panel)
    panel_message_id = id_panel.message_id

    db.add_id_panel(user_id=user_id, id=panel_message_id)
    db.disconnect()