
from random import choice
import requests

import states.states
from config_reader import gpt_tokens

from spawnbot import bot

import states.states

from db.database import db

from config_reader import proxy_config
import concurrent.futures

from time import time
from utils.decode_any_format import TYPE_TXT_FILE

async def write_book():
    ...


async def file_request(chunks, message, settings):
    db.connect()
    start_time = time()
    user_id = message.from_user.id
    degree = db.get_degree(user_id)
    if settings == None:
        settings = db.get_settings(user_id)

    answers = []
    print(settings)
    proxy = proxy_config()
    db.disconnect()

    msg = await message.answer(f'<b>Процесс работы:</b> <i>0/{len(chunks)}</i>')
    result: bool = await bot.send_chat_action(user_id, 'typing')
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:

            future = [executor.submit(solo_request, chunk, message, degree, settings, proxy) for chunk in chunks]
            for future in concurrent.futures.as_completed(future):
                answer = str(future.result()[1]).replace('\n', '. ')
                answers.append(answer)
                if len(answers) % 10 == 0:
                    await _update_progress(answers, chunks, message, msg)
                    result: bool = await bot.send_chat_action(user_id, 'typing')
                    if states.states.stop_gpt:
                        states.states.stop_gpt = False
                        result: bool = await bot.send_chat_action(message.from_user.id, 'upload_document')
                        executor.shutdown(wait=True, cancel_futures=True)
                        await _handle_exception(answers, message)
                        return [round(time() - start_time, 2), answers]
    except Exception as e:
        print(e)
        print('Выдаю файл...')
        return [round(time() - start_time, 2), answers]

    await _update_progress(answers, chunks, message, msg)
    await _handle_exception(answers, message)
    return [round(time() - start_time, 2), answers]


async def _update_progress(answers, chunks, message, msg):
    try:
        new_text = f'<b>Процесс работы:</b> <i>{len(answers)}/{len(chunks)}</i>'
        if msg.text != new_text:
            await bot.edit_message_text(new_text,
                                         chat_id=message.from_user.id,
                                         message_id=msg.message_id)
    except Exception as e:
        print(e)


async def _handle_stop_gpt(answers, message):
    states.states.stop_gpt = False
    with open(f"txt files/GPT{message.document.file_name.rsplit('.', 1)[0] + '.txt'}", "w", encoding=TYPE_TXT_FILE or "utf-8") as file:
        for answer in answers or 'OmniBot':
            file.write(answer + "\n\n")


async def _handle_exception(answers, message):
    with open(f"txt files/GPT{message.document.file_name.rsplit('.', 1)[0] + '.txt'}", "w", encoding=TYPE_TXT_FILE or "utf-8") as file:
        for answer in answers or 'OmniBot':
            file.write(answer + "\n\n")


def solo_request(text, message, degree, settings, proxy):
    start_time = time()
    """
    text_request does request from gpt. Single request 200 - 400
    :param text: chunk text from user file
    :param message: Message
    :return: list[float(time_answer), str(answer)]
    """

    basic_settings = 'Ты модель gpt 3-5 turbo'
    api_key = choice(gpt_tokens)
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": f"{settings or basic_settings}"},
            {"role": "user", "content": f"{text or message.text}"}
        ],
        "temperature": degree
    }

    try:

        response = requests.post(url, json=data, headers=headers, proxies=proxy or proxy_config())
        result = response.json()
    except Exception as e:
        print(e)
        return solo_request(text, message, degree, settings, proxy_config())

    if response.status_code == 200:
        answer = result['choices'][0]['message']['content']
        print(answer)
        return round(time() - start_time,2), answer
    else:
        return solo_request(text, message, degree, settings, proxy_config())
