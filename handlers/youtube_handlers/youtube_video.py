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
from utils.download_subtitles import download_video_subtitles
from utils.sort_file import sort_and_filter
from utils.decode_any_format import detect_file_format
import shutil
from utils.split_text_for_gpt import split_text
from utils.speech_requests import file_request
from utils.create_download_link import upload_to_fileio


youtube_video_router = Router()


@youtube_video_router.message(F.text == '🎞 Видео')
async def process_message_gpt_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    await state.set_state(WaitingYoutube.video)
    await bot.send_message(user_id, '<b>Ожидается ссылка на видео</b>')


@youtube_video_router.message(WaitingYoutube.video)
async def process_video_subtitles(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    result: bool = await bot.send_chat_action(message.from_user.id, 'typing')
    answer = download_video_subtitles(message.text)
    file_name = answer+ '.txt'
    document = FSInputFile("subtitles/"+file_name)
    await bot.send_document(message.chat.id, document)
    shutil.rmtree('subtitles')
    os.makedirs('subtitles')
    await state.clear()
