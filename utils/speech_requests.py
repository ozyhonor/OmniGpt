from random import choice
import requests
import states.states
from config_reader import gpt_tokens

from spawnbot import bot

import states.states
from db.database import db
import os
from config_reader import proxy_config
import concurrent.futures
from time import time
from time import time
from utils.decode_any_format import TYPE_TXT_FILE
from moviepy.editor import AudioFileClip, concatenate_audioclips


attempts = 0


def openai_audio_request(voice, input_text, output_file, speed, proxy=proxy_config(), model='tts-1'):
    global attempts
    start_time = time()
    api_key = choice(gpt_tokens)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    url = "https://api.openai.com/v1/audio/speech"
    data = {
        "model": model,
        "voice": voice,
        "input": input_text,
        "speed": speed
    }
    try:
        response = requests.post(url, json=data, headers=headers, stream=True, proxies=proxy)
        response.raise_for_status()
        with open(output_file, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(e)

    return [output_file, round(time()-start_time,2)]


#model, voice, input_text, output_file, speed
async def file_request(chunks, message):
    db.connect()
    start_time = time()
    user_id = message.from_user.id
    voice = db.get_voice(user_id)
    rate = db.get_rate(user_id)
    db.disconnect()
    answers = []
    proxy = proxy_config()


    msg = await message.answer(f'<b>Процесс работы:</b> <i>0/{len(chunks)}</i>')
    result: bool = await bot.send_chat_action(user_id, 'record_voice')
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:

            future = [executor.submit(openai_audio_request, voice, chunk, f'audio_files/{name}.mp3', rate, proxy_config()) for name,chunk in enumerate(chunks)]
            for future in concurrent.futures.as_completed(future):
                answer = str(future.result()[0])
                answers.append(answer)
                if len(answers) % 10 == 0:
                    await _update_progress(answers, chunks, message, msg)
                    result: bool = await bot.send_chat_action(user_id, 'record_voice')
                    if states.states.stop_gpt:
                        states.states.stop_gpt = False
                        result: bool = await bot.send_chat_action(message.from_user.id, 'upload_audio')
                        executor.shutdown(wait=True, cancel_futures=True)
                        await _handle_exception(answers, message)
                        await complete_audio_files(answers)
                        return [round(time() - start_time, 2), answers]
    except Exception as e:
        print(e)
        print('Выдаю файл...')
        await complete_audio_files(answers[0])
        return [round(time() - start_time, 2), answers]
    await _update_progress(answers, chunks, message, msg)
    await _handle_exception(answers, message)
    await complete_audio_files(answers)
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

async def complete_audio_files(files, input_folder="audio_files"):
    output_file = "audio_files/output.mp3"

    print(files)

    # Извлекаем имена файлов из путей
    file_names = [os.path.basename(file) for file in files]

    # Сортируем файлы по числовым значениям в их названиях
    sorted_mp3_files = sorted(file_names, key=lambda x: int(os.path.splitext(x)[0]))

    print(sorted_mp3_files)

    clips = [AudioFileClip('audio_files/'+file) for file in sorted_mp3_files]

    final_clip = concatenate_audioclips(clips)
    final_clip.write_audiofile(output_file, codec="mp3")

async def _handle_stop_gpt(answers, message):
    states.states.stop_gpt = False
    with open(f"txt files/GPT{message.document.file_name.rsplit('.', 1)[0] + '.txt'}", "w", encoding=TYPE_TXT_FILE or "utf-8") as file:
        for answer in answers or 'OmniBot':
            file.write(answer + "\n\n")


async def _handle_exception(answers, message):
    with open(f"txt files/GPT{message.document.file_name.rsplit('.', 1)[0] + '.txt'}", "w", encoding=TYPE_TXT_FILE or "utf-8") as file:
        for answer in answers or 'OmniBot':
            file.write(answer + "\n\n")
