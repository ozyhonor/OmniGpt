from spawnbot import bot
from aiogram import Router
from  db.database import db
from aiogram.types import Message
from states.states import WaitingStateVideoSettings
from aiogram.fsm.context import FSMContext
from menu import texts
from aiogram import types
from utils.video.create_example_video import create_example_video_async
from utils.is_color import is_hex_color
from menu.keyboards import CustomKeyboard
import os
import re

video_settings_router = Router()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'video_settings' or
                                                             callback_query.data == 'back_resolution')
async def video_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_video_settings()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()

@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'subtitles' or
                                                             callback_query.data == 'back_size' or
                                                             callback_query.data == 'back_color')
async def subtitles_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_subtitles_settings()
    button_text = callback_query.message.reply_markup.inline_keyboard[0][1].text
    if callback_query.data == 'subtitles' and button_text == '🔹Субтитры':
        db.add_subtitles(user_id, not(db.get_subtitles(user_id)))
        new_text = await reload_settings(user_id)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()




@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'translator' or
                                                             callback_query.data == 'back_language_translated' or
                                                             callback_query.data == 'back_original_lang')
async def translator_settings(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    db.connect()
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_translator_settings()
    button_text = callback_query.message.reply_markup.inline_keyboard[0][2].text
    if callback_query.data == 'translator' and button_text == '🔹Перевод':
        db.add_translator(user_id, not(db.get_translator(user_id)))
        new_text = await reload_settings(user_id)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('color:'))
async def process_color_button(callback_query: types.CallbackQuery):
    db.connect()
    color = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    db.add_color(user_id=user_id, color=color)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=CustomKeyboard.inline_color())
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'translated_language')
async def process_translated_language(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_translated_languages()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'music')
async def process_music_frame(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.create_music_frame()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)
    db.disconnect()


async def send_good_in_callback(callback_query: types.CallbackQuery):
    await callback_query.answer('Вау')


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'volume_music')
async def process_volume_music_button(callback_query: types.CallbackQuery, state: FSMContext):
    db.connect()
    await state.set_state(WaitingStateVideoSettings.volume_music)
    user_id = callback_query.from_user.id
    await callback_query.answer('Введите значение от 1 до 100')
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'interesting_moment')
async def process_interesting_moment_button(callback_query: types.CallbackQuery, state: FSMContext):
    db.connect()
    dict_bool = {1 : '✅', 0 : '❌'}
    await state.set_state(WaitingStateVideoSettings.volume_music)
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    interesting_moment_value = db.get_user_settings('interesting_moment', user_id)
    db.update_user_settings('interesting_moment', not(interesting_moment_value), user_id)
    await callback_query.answer(f'Интересные моменты AI {dict_bool[not(interesting_moment_value)]}')
    db.disconnect()

@video_settings_router.message(WaitingStateVideoSettings.volume_music)
async def change_volume_music(message: Message, state: FSMContext):
    db.connect()
    user_id = message.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_video_settings()
    db.update_user_settings('volume_music', message.text, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    await message.delete()
    await state.clear()
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('music:'))
async def process_music(callback_query: types.CallbackQuery):
    db.connect()
    music = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    db.add_music(user_id=user_id, music=music)
    markup = CustomKeyboard.create_music_frame()
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()



@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('resolution:'))
async def process_resolution(callback_query: types.CallbackQuery):
    db.connect()
    resolution = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    db.add_resolution(user_id=user_id, resolution=resolution)
    markup = CustomKeyboard.inline_resolution()
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()

@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'resolution')
async def change_resolution(callback_query: types.CallbackQuery, state: FSMContext):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_resolution()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'hex_code')
async def hex_code_button(callback_query: types.CallbackQuery, state: FSMContext):
    db.connect()
    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается HEX код цвета.', reply_markup=markup)
    await state.set_state(WaitingStateVideoSettings.color)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'hex_code_shadow')
async def hex_code_shadow_button(callback_query: types.CallbackQuery, state: FSMContext):
    db.connect()
    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается HEX код цвета.', reply_markup=markup)
    db.disconnect()
    await state.set_state(WaitingStateVideoSettings.shadow_color)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'hex_code_outline')
async def hex_code_outline_button(callback_query: types.CallbackQuery, state: FSMContext):
    db.connect()
    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается HEX код цвета.', reply_markup=markup)
    await state.set_state(WaitingStateVideoSettings.outline_color)
    db.disconnect()

@video_settings_router.message(WaitingStateVideoSettings.outline_color)
async def change_outline_color(message: Message, state: FSMContext):
    db.connect()
    user_id = message.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_outline_color()
    if is_hex_color(message.text):
        db.add_outline_color(message.from_user.id, message.text[::-1])
        new_text = await reload_settings(user_id)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
        await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await state.clear()
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'video_cancel')
async def cancel_button(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback_query.from_user.id

    data = await state.get_data()
    previous_message_id = data.get('previous_message_id')

    if previous_message_id:
        await bot.delete_message(chat_id=user_id, message_id=previous_message_id)

    await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
    await state.clear()



@video_settings_router.message(WaitingStateVideoSettings.color)
async def change_color(message: Message, state: FSMContext):
    db.connect()
    user_id = message.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_color()
    if is_hex_color(message.text):
        db.add_color(message.from_user.id, message.text[::-1])
        new_text = await reload_settings(user_id)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
        await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await state.clear()
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('position:'))
async def process_position_button(callback_query: types.CallbackQuery):
    db.connect()
    position = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    db.add_position(user_id=user_id, position=position)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=CustomKeyboard.inline_position())
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'position')
async def process_position(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_position()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'x_y_subtitles')
async def coorgs_code_button(callback_query: types.CallbackQuery, state: FSMContext):
    db.connect()
    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается высота,ширина.', reply_markup=markup)
    db.disconnect()
    await state.set_state(WaitingStateVideoSettings.position)


@video_settings_router.message(WaitingStateVideoSettings.position)
async def change_position(message: Message, state: FSMContext):
    db.connect()
    user_id = message.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_position()
    try:
        position = int((message.text).split(',')[0]) , int(message.text.split(',')[1])
        db.add_position(message.from_user.id, message.text)
        new_text = await reload_settings(user_id)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
        await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    except:
        ...
    await message.delete()
    db.disconnect()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await state.clear()


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('size:'))
async def process_size_button(callback_query: types.CallbackQuery):
    db.connect()
    size = int(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    db.add_size(user_id=user_id, size=size)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=CustomKeyboard.inline_size())
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'size')
async def size_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_size()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'font')
async def font_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_font()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)
    db.disconnect()




@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'upload_music')
async def music_add_button(callback_query: types.CallbackQuery, state: FSMContext):
    db.connect()
    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается аудиофайл. mp3, wav, acc.', reply_markup=markup)
    await state.set_state(WaitingStateVideoSettings.music)
    db.disconnect()


@video_settings_router.message(WaitingStateVideoSettings.music)
async def upload_document_music(message: Message, state: FSMContext):
    db.connect()
    user_id = message.from_user.id
    panel_id = db.get_id_panel(user_id)
    result: bool = await bot.send_chat_action(message.from_user.id, 'upload_audio')
    file_id = message.audio.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    main_file_name = os.path.join('music', message.audio.file_name)
    file_ext = os.path.splitext(main_file_name)[1]
    db.disconnect()

    if file_ext.lower() in ['.mp3', '.wav', '.acc']:
        music = await bot.download_file(file_path, main_file_name)
        print(message.text)
        markup = CustomKeyboard.create_music_frame()
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)

    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await state.clear()







@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('font:'))
async def process_font_button(callback_query: types.CallbackQuery):
    db.connect()
    font = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    db.add_font(user_id=user_id, font=font)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=CustomKeyboard.inline_font())
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'upload_font')
async def font_button(callback_query: types.CallbackQuery, state: FSMContext):
    db.connect()
    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается файл шрифта. ttf, otf, woff, woff2.', reply_markup=markup)
    await state.set_state(WaitingStateVideoSettings.font)
    db.disconnect()


@video_settings_router.message(WaitingStateVideoSettings.font)
async def change_font(message: Message, state: FSMContext):
    db.connect()
    user_id = message.from_user.id
    panel_id = db.get_id_panel(user_id)
    result: bool = await bot.send_chat_action(message.from_user.id, 'upload_document')
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    main_file_name = os.path.join('fonts', message.document.file_name)
    file_ext = os.path.splitext(main_file_name)[1]
    db.disconnect()

    if file_ext.lower() in ['.ttf', '.otf', '.woff', '.woff2']:
        font = await bot.download_file(file_path, main_file_name)
        markup = CustomKeyboard.inline_font()
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)

    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await state.clear()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'color')
async def color_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_color()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'outline')
async def outline_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_subtitles_settings()
    outline = db.get_outline(user_id)
    db.add_outline(user_id=user_id, outline=not(outline))
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()

@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'smart_subtitles')
async def change_smart_srt(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_subtitles_settings()
    smart_srt = db.get_smart_sub(user_id)
    db.add_smart_sub(user_id=user_id, smart_sub=not(smart_srt))
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()

@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'shadow')
async def shadow_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_subtitles_settings()
    shadow = db.get_shadow(user_id)
    db.add_shadow(user_id=user_id, shadow=not(shadow))
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'color_shadow')
async def shadow_color_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_shadow_color()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'color_outline')
async def color_outline_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_outline_color()
    db.disconnect()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'size_shadow')
async def size_shadow_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    db.disconnect()
    markup = CustomKeyboard.inline_size_shadow()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)

@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'max_words')
async def max_words_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_max_words()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()

@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('max_words:'))
async def process_max_words_button(callback_query: types.CallbackQuery):
    db.connect()
    max_words = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_max_words()
    db.add_max_words(user_id=user_id, max_words=max_words)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('shadow_size:'))
async def process_shadow_size_button(callback_query: types.CallbackQuery):
    db.connect()
    size = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_size_shadow()
    db.add_shadow_size(user_id=user_id, shadow_size=size)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()

@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('outline_color:'))
async def process_outline_color_button(callback_query: types.CallbackQuery):
    db.connect()
    color = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_outline_color()
    db.add_outline_color(user_id=user_id, outline_color=color)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()



@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('shadow_color:'))
async def process_shadow_color_button(callback_query: types.CallbackQuery):
    db.connect()
    color = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_shadow_color()
    db.add_shadow_color(user_id=user_id, shadow_color=color)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'size_outline')
async def size_outline_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_outline_size()
    outline = db.get_outline(user_id)
    db.add_outline(user_id=user_id, outline=not(outline))
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('outline_size:'))
async def process_outline_size_button(callback_query: types.CallbackQuery):
    db.connect()
    size = int(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_outline_size()
    db.add_outline_size(user_id=user_id, outline_size=size)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()



@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('translated_language:'))
async def process_translated_language(callback_query: types.CallbackQuery):
    db.connect()
    lang = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_translated_languages()
    db.add_translated_language(user_id=user_id, translated_language=lang)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'original_speed')
async def original_speed_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_original_speed()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'translated_speed')
async def translated_speed_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_translated_speed()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('translated_speed:'))
async def process_translated_speed_button(callback_query: types.CallbackQuery):
    db.connect()
    speed = float(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_translated_speed()
    db.add_translation_speed(user_id=user_id, translation_speed=speed)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()



@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('original_speed:'))
async def process_original_speed_button(callback_query: types.CallbackQuery):
    db.connect()
    speed = float(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_original_speed()
    db.add_original_speed(user_id=user_id, original_speed=speed)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()
#CROOOOOOOP


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('cancel_stamp:'))
async def process_delite_one_crop_button(callback_query: types.CallbackQuery):
    db.connect()
    deliting = str(callback_query.data.split(';')[1])
    print(deliting)
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)

    timestamps = db.get_timestamps(user_id=user_id).split(' ')
    len_temp = len(timestamps)

    timestamps.remove(deliting)
    timestamps_str = ' '.join(timestamps)
    if len_temp == 1:
        db.add_timestamps(user_id=user_id, timestamps='0')
    else:
        db.add_timestamps(user_id=user_id, timestamps=timestamps_str)
    timestamps = db.get_timestamps(user_id=user_id).split(' ')
    markup = CustomKeyboard.inline_crop_menu(timestamps)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'timestamps')
async def crop_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    timestamps = str(db.get_timestamps(user_id)).split(' ')
    markup = CustomKeyboard.inline_crop_menu(timestamps)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'add_new_stamp')
async def crop_add_settings(callback_query: types.CallbackQuery,state: FSMContext):
    db.connect()
    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text=texts.video_stamps, reply_markup=markup)
    db.disconnect()
    await state.set_state(WaitingStateVideoSettings.timestamps)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'clear_all_stamp')
async def clear_stamps_settings(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    timestamps = str(db.get_timestamps(user_id)).split(' ')
    db.add_timestamps(user_id=user_id, timestamps='0')
    timestamps = str(db.get_timestamps(user_id)).split(' ')
    markup = CustomKeyboard.inline_crop_menu(timestamps)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    db.disconnect()



@video_settings_router.message(WaitingStateVideoSettings.timestamps)
async def change_timestamps(message: Message, state: FSMContext):
    db.connect()
    user_id = message.from_user.id
    panel_id = db.get_id_panel(user_id)

    stamps = message.text.split(' ')

    pattern = r'^(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})$'

    for timestamp in stamps:
        old_stamps = db.get_timestamps(user_id)
        if re.match(pattern, timestamp):
            if old_stamps != '0':
                print(old_stamps, timestamp)
                db.add_timestamps(user_id=user_id, timestamps=f'{old_stamps} '+timestamp)
            else:
                db.add_timestamps(user_id=user_id, timestamps=timestamp)

    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    markup = CustomKeyboard.inline_crop_menu(str(db.get_timestamps(user_id=user_id)).split(' '))
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)
    db.disconnect()
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await state.clear()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'example')
async def do_example_button(callback_query: types.CallbackQuery):
    db.connect()
    user_id = callback_query.from_user.id
    panel_id = db.get_id_panel(user_id)
    db.disconnect()

    await create_example_video_async(user_id)





async def reload_settings(user_id):
    dict_bool = {1 : '✅', 0 : '❌'}
    languages = {
        'en': '🇬🇧',
        'es': '🇪🇸',
        'fr': '🇫🇷',
        'ru': '🇷🇺',
        'zh-cn': '🇨🇳',
        'ar': '🇸🇦',
        'pt': '🇵🇹',
        'de': '🇩🇪',
        'ja': '🇯🇵',
        'hi': '🇮🇳',
        'it': '🇮🇹',
        'ko': '🇰🇷'
    }
    music = db.get_music(user_id)
    video_title = db.get_video_title(user_id)
    resolution = db.get_resolution(user_id)
    subtitles = dict_bool[db.get_subtitles(user_id)]
    font = db.get_font(user_id)
    size = db.get_size(user_id)
    color = db.get_color(user_id)
    position = db.get_position(user_id)
    outline = dict_bool[db.get_outline(user_id)]
    outline_size = db.get_outline_size(user_id)
    outline_color = db.get_outline_color(user_id)
    shadow = dict_bool[db.get_shadow(user_id)]
    shadow_size = db.get_shadow_size(user_id)
    shadow_color = db.get_shadow_color(user_id)
    translator = dict_bool[db.get_translator(user_id)]
    source_language = db.get_source_language(user_id)
    translated_language = db.get_translated_language(user_id) + languages[db.get_translated_language(user_id)]
    original_speed = db.get_original_speed(user_id)
    translation_speed = db.get_translation_speed(user_id)
    max_words = db.get_max_words(user_id)
    smart_sub = dict_bool[db.get_smart_sub(user_id)]
    timestamps = db.get_timestamps(user_id)
    music_volume = db.get_user_settings('volume_music', user_id)

    # Форматирование строки с настройками видео
    new_settings = texts.video_settings_message.format(
        music=music,
        music_volume=music_volume,
        video_title=video_title,
        resolution=resolution,
        subtitles=subtitles,
        font=font,
        size=size,
        color=color,
        position=position,
        outline=outline,
        outline_size=outline_size,
        outline_color=outline_color,
        shadow=shadow,
        shadow_size=shadow_size,
        shadow_color=shadow_color,
        translator=translator,
        source_language=source_language,
        translated_language=translated_language,
        original_speed=original_speed,
        translation_speed=translation_speed,
        max_words=max_words,
        smart_sub=smart_sub,
        timestamps=timestamps
    )
    return new_settings
