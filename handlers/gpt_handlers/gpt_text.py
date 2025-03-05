import traceback
from aiogram.types.input_file import FSInputFile
import os
from aiogram import Router, F
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingStateGpt
from spawnbot import bot
from menu import texts
from utils.latex_to_unicode import convert_latex_to_unicode
import re
from datetime import datetime
from utils.gpt_requests import solo_request


gpt_text = Router()

@gpt_text.message(F.text == '🗒 Текст')
async def process_message_gpt_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(WaitingStateGpt.text_gpt)
    user_id = message.from_user.id
    await bot.send_message(user_id, '<b>Ожидается текстовый запрос</b>')


@gpt_text.message(WaitingStateGpt.text_gpt)
async def go_gpt_text_request(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    degree = await db.get_user_setting('degree', user_id)
    model = await db.get_user_setting('gpt_model', user_id)
    await bot.send_chat_action(user_id, 'typing')
    answer = await solo_request(None, message, degree, None, model)
    print(answer[1])
    cleared_answer = await convert_latex_to_unicode(answer[1])

    await message.answer(texts.water_mark_omnigpt.format(answer[2]))
    try:
        # Проверяем длину текста
        cleared_answer_str = str(cleared_answer)
        if len(cleared_answer_str) > 4000:
            # Если текст слишком длинный, сохраняем в файл и отправляем

            file_path = f'{re.sub(r'[:\-]', '_', str(datetime.now()).split('.')[0])}.txt'

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(cleared_answer_str)

            document = FSInputFile(file_path)
            await bot.send_document(message.chat.id, document)
            os.remove(file_path)
        else:
            await message.answer(cleared_answer_str, parse_mode="Markdown")

    except:
        print(traceback.format_exc())



    await state.clear()
