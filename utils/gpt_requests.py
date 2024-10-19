from random import choice
import requests
import traceback
import states.states
import re
from config_reader import gpt_tokens

from spawnbot import bot

import states.states

from db.database import db

from config_reader import proxy_config
import concurrent.futures
from time import time
import asyncio
import aiohttp
from setup_logger import logger
from utils.decode_any_format import TYPE_TXT_FILE
from collections import defaultdict


async def write_book():
    ...



async def chunks_request(chunks, message, settings, post_request=''):
    start_time = time()
    used_tokens = 0
    user_id = message.from_user.id
    degree = await db.get_user_setting('degree', user_id)


    model = await db.get_user_setting('gpt_model', user_id)
    if post_request:
        model = await db.get_user_setting('gpt_model', user_id)

    if settings is None:
        settings = await db.get_user_setting('gpt', user_id)

    # Создаем список для хранения ответов в правильном порядке
    answers = [None] * len(chunks)

    # Отправляем первоначальное сообщение с прогрессом
    progress_msg = await message.answer(f'<b>Процесс работы:</b> <i>0/{len(chunks)}</i>')
    last_update_time = time()
    try:
        await bot.send_chat_action(user_id, 'typing')
        # Создаем задачи и сохраняем их в словаре с индексами
        tasks = {
            i: asyncio.create_task(solo_request(chunk, message, degree, settings, model))
            for i, chunk in enumerate(chunks)
        }

        # Ожидаем выполнения всех задач и сохраняем результаты в правильном порядке
        for i, task in tasks.items():
            result = await task
            used_tokens += int(result[2])
            answers[i] = str(result[1])  # сохраняем ответ в соответствующую позицию
            current_time = time()
            # Обновляем прогресс каждые 10 задач
            if (i + 1) % 10 == 0 or (current_time - last_update_time) >= 5:
                await _update_progress(answers, chunks, message, progress_msg)
                last_update_time = current_time  # Сбрасываем таймер обновления


                try:
                    await bot.send_chat_action(user_id, 'typing')
                except Exception as e:
                    logger.error(e)

                if states.states.stop_gpt:
                    await _handle_stop_gpt(answers, message)
                    return [round(time() - start_time, 2), answers, used_tokens]

    except Exception as e:
        print(f"Ошибка: {e}")
        return [round(time() - start_time, 2), used_tokens, used_tokens]

    # Завершаем процесс, обновляем прогресс и сохраняем результат
    await _update_progress(answers, chunks, message, progress_msg)

    await _handle_exception(answers, message, post_request)
    return [round(time() - start_time, 2), answers, used_tokens]


# Асинхронная функция для обновления прогресса
async def _update_progress(answers, chunks, message, msg):
    try:
        new_text = f'<b>Процесс работы:</b> <i>{len(answers)}/{len(chunks)}</i>'
        if msg.text != new_text:
            await bot.edit_message_text(new_text, chat_id=message.from_user.id, message_id=msg.message_id)
    except Exception as e:
        print(f"Ошибка обновления прогресса: {e}")


# Асинхронная функция для обработки остановки GPT
async def _handle_stop_gpt(answers, message):
    try:
        states.states.stop_gpt = False
        await _save_answers_to_file(answers, message, "upload_document")
    except:
        ...

# Асинхронная функция для обработки исключений и сохранения результатов
async def _handle_exception(answers, message, post = ''):
    try:
        if post:
            answers = reversed(sorted(answers, key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+',
                                                                                                             x) and 0 <= int(
                re.search(r'\d+', x).group()) <= 10 else float('-inf')))

        await _save_answers_to_file(answers, message, "OmniBot",post)
    except:
        ...


# Функция для сохранения ответов в файл
async def _save_answers_to_file(answers, message, default_name,post=''):
    try:
        file_name = f"txt files/{post}GPT{message.document.file_name.rsplit('.', 1)[0]}.txt"
        with open(file_name, "w", encoding=TYPE_TXT_FILE or "utf-8") as file:
            for answer in answers or default_name:
                file.write(answer + "\n\n")
    except:
        ...

async def solo_request(text, message, degree, settings, model='gpt-3.5-turbo', max_retries=4):
    start_time = time()

    async def make_request(session, attempt, text):
        proxy = proxy_config().get('https')
        logger.info(f"Attempt {attempt} for request.")
        basic_settings = f'Ты модель {model}'
        api_key = choice(gpt_tokens)
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": f"{model}",
            "messages": [
                {"role": "system", "content": f"{settings or basic_settings}"},
                {"role": "user", "content": f"{text or message.text}"}
            ],
            "temperature": degree
        }
        try:
            async with session.post(url, json=data, headers=headers, proxy=proxy) as response:
                result = await response.json()
                status = response.status
                text = await response.text()
                print(text)

                answer = result['choices'][0]['message']['content']
                tokens_used = result['usage']['total_tokens']
                logger.info(f"Request successful: {tokens_used} tokens used.")
                return round(time() - start_time, 2), answer, tokens_used

        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            return None, '', None

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        for attempt in range(1, max_retries + 1):
            time_taken, answer, tokens_used = await make_request(session, attempt, text)
            if answer:
                print(answer)
                return time_taken, answer, tokens_used
            logger.warning(f"Retrying... ({attempt}/{max_retries})")

    logger.error("Max retries reached. Request failed.")
    return None, '', None

