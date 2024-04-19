from aiogram import Router, F
from aiogram.types import Message
import states.states
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from states.states import WaitingYoutube
from spawnbot import bot
from menu import keyboards, texts
import os
from utils.download_subtitles import all_files_in_one
from utils.download_subtitles import download_playlist_subtitles
from utils.sort_file import sort_and_filter
from utils.decode_any_format import detect_file_format
import shutil
from utils.split_text_for_gpt import split_text
from utils.speech_requests import file_request
from utils.create_download_link import upload_to_fileio


youtube_playlist_router = Router()


@youtube_playlist_router.message(F.text == '💽 Плейлист')
async def process_message_gpt_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    await state.set_state(WaitingYoutube.playlist)
    await bot.send_message(user_id, '<b>Ожидается ссылка на плейлист</b>')


@youtube_playlist_router.message(WaitingYoutube.playlist)
async def process_playlist_subtitles(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    result: bool = await bot.send_chat_action(message.from_user.id, 'typing')
    answer = await download_playlist_subtitles(message.text, user_id, message)
    all_files_in_one()
    file_name = 'объединенный_файл.txt'
    document = FSInputFile(file_name)
    await bot.send_document(message.chat.id, document)
    os.remove('объединенный_файл.txt')
    shutil.rmtree('subtitles')
    os.makedirs('subtitles')
    await state.clear()
