from spawnbot import bot
from aiogram import Router, F
from  db.database import db
import asyncio
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


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'sample_video')
async def go_to_listen_new_sample(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback_query.from_user.id
    await state.set_state(WaitingStateVideoSettings.sample)
    await callback_query.answer('Ожидается шаблон настроек')


@video_settings_router.message(WaitingStateVideoSettings.sample)
async def process_sample(message: Message, state: FSMContext):
    dict_bool = {'✅': 1, '❌': 0}
    changed_settings = {}
    markup = CustomKeyboard.create_inline_video_settings_buttons()
    message_text = message.text
    user_id = message.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)

    for key, pattern in texts.settings_sample_pattern.items():
        match = pattern.search(message_text)
        if match:
            value = match.group(1)
            if value in {'✅', '❌'}:
                value = dict_bool[value]
            changed_settings[key] = value
            await db.update_user_setting(key, value, user_id)

    new_text = await reload_settings(user_id)
    await bot.delete_message(message_id=message.message_id, chat_id=user_id)
    await bot.edit_message_text(new_text, chat_id=user_id, message_id=panel_id)
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)
    await state.clear()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'video_settings' or
                                                             callback_query.data == 'back_resolution')
async def video_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_video_settings()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'subtitles' or
                                                             callback_query.data == 'back_size' or
                                                             callback_query.data == 'back_color')
async def subtitles_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_subtitles_settings()
    button_text = callback_query.message.reply_markup.inline_keyboard[0][1].text
    if callback_query.data == 'subtitles' and button_text == '🔹Субтитры':
        inverse_subtitles = not(await db.get_user_setting('subtitles', user_id))
        await db.update_user_setting('subtitles', inverse_subtitles, user_id)
        new_text = await reload_settings(user_id)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)




@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'translator' or
                                                             callback_query.data == 'back_language_translated' or
                                                             callback_query.data == 'back_original_lang')
async def translator_settings(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_translator_settings()
    button_text = callback_query.message.reply_markup.inline_keyboard[0][2].text
    if callback_query.data == 'translator' and button_text == '🔹Перевод':
        inverse_translator = not(await db.get_user_setting('translator', user_id))
        await db.update_user_setting('translator', inverse_translator, user_id)
        new_text = await reload_settings(user_id)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data=='overlap')
async def process_overlap_button(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_overlap_change()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)

@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('overlap:'))
async def process_overlap_value_button(callback_query: types.CallbackQuery):

    overlap = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    await db.update_user_setting(key='overlap', value=overlap, user_id=user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=CustomKeyboard.inline_overlap_change())


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('color:'))
async def process_color_button(callback_query: types.CallbackQuery):

    color = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    await db.update_user_setting('color',color, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=CustomKeyboard.inline_color())


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'translated_language')
async def process_translated_language(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_translated_languages()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'music')
async def process_music_frame(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.create_music_frame()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)

@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'volume_music')
async def process_volume_music_button(callback_query: types.CallbackQuery, state: FSMContext):

    await state.set_state(WaitingStateVideoSettings.volume_music)
    user_id = callback_query.from_user.id
    await callback_query.answer('Введите значение от 1 до 100')


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'interesting_moment')
async def process_interesting_moment_button(callback_query: types.CallbackQuery, state: FSMContext):

    dict_bool = {1 : '✅', 0 : '❌'}
    await state.set_state(WaitingStateVideoSettings.volume_music)
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    interesting_moment_value = await db.get_user_setting('interesting_moment', user_id)
    await db.update_user_setting('interesting_moment', not(interesting_moment_value), user_id)
    await callback_query.answer(f'Интересные моменты AI {dict_bool[not(interesting_moment_value)]}')

@video_settings_router.message(WaitingStateVideoSettings.volume_music)
async def change_volume_music(message: Message, state: FSMContext):

    user_id = message.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_video_settings()
    await db.update_user_setting('volume_music', message.text, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    await message.delete()
    await state.clear()


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('music:'))
async def process_music(callback_query: types.CallbackQuery):

    music = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    await db.update_user_setting('music', music, user_id=user_id)
    markup = CustomKeyboard.create_music_frame()
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)



@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('resolution:'))
async def process_resolution(callback_query: types.CallbackQuery):

    resolution = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    await db.update_user_setting('resolution', resolution, user_id=user_id)
    markup = CustomKeyboard.inline_resolution()
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'resolution')
async def change_resolution(callback_query: types.CallbackQuery, state: FSMContext):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_resolution()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'hex_code')
async def hex_code_button(callback_query: types.CallbackQuery, state: FSMContext):

    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается HEX код цвета.', reply_markup=markup)
    await state.set_state(WaitingStateVideoSettings.color)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'hex_code_shadow')
async def hex_code_shadow_button(callback_query: types.CallbackQuery, state: FSMContext):

    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается HEX код цвета.', reply_markup=markup)
    await state.set_state(WaitingStateVideoSettings.shadow_color)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'hex_code_outline')
async def hex_code_outline_button(callback_query: types.CallbackQuery, state: FSMContext):

    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается HEX код цвета.', reply_markup=markup)
    await state.set_state(WaitingStateVideoSettings.outline_color)

@video_settings_router.message(WaitingStateVideoSettings.outline_color)
async def change_outline_color(message: Message, state: FSMContext):

    user_id = message.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_outline_color()
    if is_hex_color(message.text):
        color = message.text[::-1]
        await db.update_user_setting('outline_color', color, user_id)
        new_text = await reload_settings(user_id)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
        await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await state.clear()


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

    user_id = message.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_color()
    if is_hex_color(message.text):
        color = message.text[::-1]
        await db.update_user_setting('color', color, user_id)
        new_text = await reload_settings(user_id)
        await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
        await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await state.clear()


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('position:'))
async def process_position_button(callback_query: types.CallbackQuery):

    position = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    await db.update_user_setting('position', position, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=CustomKeyboard.inline_position())


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'position')
async def process_position(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_position()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'x_y_subtitles')
async def coorgs_code_button(callback_query: types.CallbackQuery, state: FSMContext):

    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается высота,ширина.', reply_markup=markup)
    await state.set_state(WaitingStateVideoSettings.position)


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('size:'))
async def process_size_button(callback_query: types.CallbackQuery):

    size = int(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    await db.update_user_setting('size', size, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=CustomKeyboard.inline_size())


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'size')
async def size_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_size()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'font')
async def font_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_font()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)




@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'upload_music')
async def music_add_button(callback_query: types.CallbackQuery, state: FSMContext):

    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается аудиофайл. mp3, wav, acc.', reply_markup=markup)
    await state.set_state(WaitingStateVideoSettings.music)


@video_settings_router.message(WaitingStateVideoSettings.music)
async def upload_document_music(message: Message, state: FSMContext):

    user_id = message.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    result: bool = await bot.send_chat_action(message.from_user.id, 'upload_audio')
    file_id = message.audio.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    main_file_name = os.path.join('music', message.audio.file_name)
    file_ext = os.path.splitext(main_file_name)[1]

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

    font = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    await db.update_user_setting('font', font, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=CustomKeyboard.inline_font())


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'upload_font')
async def font_button(callback_query: types.CallbackQuery, state: FSMContext):

    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text='Ожидается файл шрифта. ttf, otf, woff, woff2.', reply_markup=markup)
    await state.set_state(WaitingStateVideoSettings.font)


@video_settings_router.message(WaitingStateVideoSettings.font)
async def change_font(message: Message, state: FSMContext):

    user_id = message.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    result: bool = await bot.send_chat_action(message.from_user.id, 'upload_document')
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    main_file_name = os.path.join('fonts', message.document.file_name)
    file_ext = os.path.splitext(main_file_name)[1]

    if file_ext.lower() in ['.ttf', '.otf', '.woff', '.woff2']:
        font = await bot.download_file(file_path, main_file_name)
        markup = CustomKeyboard.inline_font()
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)

    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await state.clear()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'color')
async def color_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_color()
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'outline')
async def outline_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_subtitles_settings()
    outline = not(await db.get_user_setting('outline',user_id))
    await db.update_user_setting('outline', outline, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)

@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'smart_subtitles')
async def change_smart_srt(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_subtitles_settings()
    smart_srt = not(await db.get_user_setting('smart_sub', user_id))
    await db.update_user_setting('smart_sub', smart_srt, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)

@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'shadow')
async def shadow_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_subtitles_settings()
    shadow = await db.get_user_setting('shadow', user_id)
    if shadow:
        await db.update_user_setting('shadow_color', 'transparent', user_id)
    else:
        await db.update_user_setting('shadow_color', 'black', user_id)
    await db.update_user_setting('shadow', not(shadow), user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'color_shadow')
async def shadow_color_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_shadow_color()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'color_outline')
async def color_outline_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_outline_color()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'size_shadow')
async def size_shadow_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_size_shadow()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)

@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'max_words')
async def max_words_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_max_words()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)

@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('max_words:'))
async def process_max_words_button(callback_query: types.CallbackQuery):

    max_words = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_max_words()
    await db.update_user_setting('max_words', max_words, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('shadow_size:'))
async def process_shadow_size_button(callback_query: types.CallbackQuery):

    size = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_size_shadow()
    await db.update_user_setting('shadow_size', size, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)

@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('outline_color:'))
async def process_outline_color_button(callback_query: types.CallbackQuery):

    color = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_outline_color()
    await db.update_user_setting('outline_color', color, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)



@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('shadow_color:'))
async def process_shadow_color_button(callback_query: types.CallbackQuery):

    color = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_shadow_color()
    await db.update_user_setting('shadow_color', color, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'size_outline')
async def size_outline_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_outline_size()
    outline =not( await db.get_user_setting('outline', user_id))
    await db.update_user_setting('outline', outline, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('outline_size:'))
async def process_outline_size_button(callback_query: types.CallbackQuery):

    size = int(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_outline_size()
    await db.update_user_setting('outline_size', size, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)



@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('translated_language:'))
async def process_translated_language(callback_query: types.CallbackQuery):

    lang = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_translated_languages()
    await db.update_user_setting('translated_language', lang, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'original_speed')
async def original_speed_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_original_speed()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'translated_speed')
async def translated_speed_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_translated_speed()
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('translated_speed:'))
async def process_translated_speed_button(callback_query: types.CallbackQuery):

    speed = float(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_translated_speed()
    await db.update_user_setting('translation_speed', speed, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)



@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('original_speed:'))
async def process_original_speed_button(callback_query: types.CallbackQuery):

    speed = float(callback_query.data.split(':')[1])
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_original_speed()
    await db.update_user_setting('original_speed', speed, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data.startswith('cancel_stamp:'))
async def process_delite_one_crop_button(callback_query: types.CallbackQuery):

    deliting = str(callback_query.data.split(';')[1])
    print(deliting)
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)

    timestamps = await db.get_user_setting('timestamps', user_id).split(' ')
    len_temp = len(timestamps)

    timestamps.remove(deliting)
    timestamps_str = ' '.join(timestamps)
    if len_temp == 1:
        await db.update_user_setting('timestamps', '0', user_id)
    else:
        await db.update_user_setting('timestamps', timestamps_str, user_id)
    timestamps = db.get_timestamps(user_id=user_id).split(' ')
    markup = CustomKeyboard.inline_crop_menu(timestamps)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'timestamps')
async def crop_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    timestamps = str(await db.get_user_setting('timestamps', user_id)).split(' ')
    markup = CustomKeyboard.inline_crop_menu(timestamps)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'add_new_stamp')
async def crop_add_settings(callback_query: types.CallbackQuery,state: FSMContext):

    await state.clear()
    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    markup = CustomKeyboard.inline_cancel()
    await bot.send_message(chat_id=user_id, text=texts.video_stamps, reply_markup=markup)
    await state.set_state(WaitingStateVideoSettings.timestamps)


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'clear_all_stamp')
async def clear_stamps_settings(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)
    await db.update_user_setting('timestamps', '0', user_id)
    timestamps = str(await db.get_user_setting('timestamps', user_id)).split(' ')
    markup = CustomKeyboard.inline_crop_menu(timestamps)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    await bot.edit_message_reply_markup(user_id, panel_id, reply_markup=markup)



@video_settings_router.message(WaitingStateVideoSettings.timestamps)
async def change_timestamps(message: Message, state: FSMContext):

    user_id = message.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)

    stamps = message.text.split(' ')

    pattern = r'^(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})$'

    for timestamp in stamps:
        old_stamps = str(await db.get_user_setting('timestamps', user_id))

        if re.match(pattern, timestamp):
            if old_stamps != '0':
                print(old_stamps, timestamp)
                await db.update_user_setting('timestamps', f'{old_stamps} '+timestamp, user_id)
            else:
                await db.update_user_setting('timestamps', timestamp, user_id)
    new_text = await reload_settings(user_id)
    await bot.edit_message_text(chat_id=user_id, message_id=panel_id, text=new_text)
    time_stamps = str(await db.get_user_setting('timestamps', user_id)).split(' ')
    markup = CustomKeyboard.inline_crop_menu(time_stamps)
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=panel_id, reply_markup=markup)
    await message.delete()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id - 1)
    await state.clear()


@video_settings_router.callback_query(lambda callback_query: callback_query.data == 'example')
async def do_example_button(callback_query: types.CallbackQuery):

    user_id = callback_query.from_user.id
    panel_id = await db.get_user_setting('id_settings_panel', user_id)


    await create_example_video_async(user_id)


async def apply_settings(user_id, current_text, new_settings):
    dict_bool = {1: '✅', 0: '❌'}
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

    # Обновляем текст с добавлением <blockquote> для измененных настроек
    updated_text = current_text
    for key, new_value in new_settings.items():
        pattern = texts.settings_sample_pattern.get(key)
        if pattern:
            # Формируем строку для замены
            new_line = f'{key}: {new_value}'
            highlighted_line = f'<blockquote>{new_line}</blockquote>'
            # Заменяем строку в тексте, добавляя <blockquote>
            updated_text = re.sub(pattern, highlighted_line, updated_text)

    return updated_text


async def reload_settings(user_id):
    dict_bool = {1: '✅', 0: '❌'}
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

    # Получаем все настройки с использованием новой функции
    music = await db.get_user_setting('music', user_id)
    music_volume = await db.get_user_setting('volume_music', user_id)
    video_title = await db.get_user_setting('video_title', user_id)
    resolution = await db.get_user_setting('resolution', user_id)
    subtitles = dict_bool[await db.get_user_setting('subtitles', user_id)]
    font = await db.get_user_setting('font', user_id)
    size = await db.get_user_setting('font_size', user_id)
    color = await db.get_user_setting('primary_color', user_id)
    position = await db.get_user_setting('position', user_id)
    outline = dict_bool[await db.get_user_setting('outline', user_id)]
    outline_size = await db.get_user_setting('outline_size', user_id)
    outline_color = await db.get_user_setting('outline_color', user_id)
    shadow = dict_bool[await db.get_user_setting('background', user_id)]
    shadow_color = await db.get_user_setting('background_color', user_id)
    translator = dict_bool[await db.get_user_setting('translator', user_id)]
    source_language = await db.get_user_setting('source_language', user_id)
    translated_language = await db.get_user_setting('translated_language', user_id)
    original_speed = await db.get_user_setting('original_speed', user_id)
    translation_speed = await db.get_user_setting('translation_speed', user_id)
    max_words = await db.get_user_setting('max_words', user_id)
    smart_sub = dict_bool[await db.get_user_setting('smart_sub', user_id)]
    timestamps = await db.get_user_setting('timestamps', user_id)
    overlap = await db.get_user_setting('overlap', user_id)

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
        shadow_color=shadow_color,
        translator=translator,
        source_language=source_language,
        translated_language=translated_language,
        original_speed=original_speed,
        translation_speed=translation_speed,
        overlap=overlap,
        max_words=max_words,
        smart_sub=smart_sub,
        timestamps=timestamps
    )

    return new_settings