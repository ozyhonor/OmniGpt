from random import choice
import requests
import states.states
from config_reader import gpt_tokens

from spawnbot import bot
from concurrent.futures import CancelledError
import asyncio
import states.states
from db.database import db
import os
from config_reader import proxy_config
import concurrent.futures
from time import time
from time import time
from utils.decode_any_format import TYPE_TXT_FILE
from moviepy.editor import AudioFileClip, concatenate_audioclips

import aiohttp
import aiofiles
from time import time
from random import choice
from setup_logger import logger


async def openai_audio_request(voice, input_text, output_file, speed, model='tts-1'):

    max_attempts = 4
    attempts = 0
    start_time = time()

    while attempts < max_attempts:
        proxy = proxy_config().get('https')
        attempts += 1
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
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.post(url, json=data, headers=headers,
                                        proxy=str(proxy) if proxy else None) as response:
                    response.raise_for_status()
                    content = await response.read()
                    async with aiofiles.open(output_file, 'wb') as file:
                        await file.write(content)

                    logger.info(f"Request successful on attempt {attempts}. Output saved to {output_file}")

                    try:
                        result = await response.json()
                        tokens_used = result['usage']['total_tokens']
                    except:
                        tokens_used = 10
                        logger.warning('Its not working li63')
                    return [output_file, tokens_used, round(time() - start_time, 2)]

        except Exception as e:
            logger.error(f"Attempt {attempts} failed: {e}")
            if attempts >= max_attempts:
                logger.error("Maximum number of attempts reached. Request failed")



#model, voice, input_text, output_file, speed
async def file_request(chunks, message):
    start_time = time()
    user_id = message.from_user.id
    token_coast = 10
    voice = await db.get_user_setting('synthes_voice',user_id)
    rate = await db.get_user_setting('synthes_speed',user_id)

    answers = []

    msg = await message.answer(f'<b>Процесс работы:</b> <i>0/{len(chunks)}</i>')
    await bot.send_chat_action(user_id, 'record_voice')

    try:
        tasks = [
            openai_audio_request(voice, chunk, f'audio_files/{name}.mp3', rate)
            for name, chunk in enumerate(chunks)
        ]

        for i, task in enumerate(asyncio.as_completed(tasks)):
            try:
                solo_request_answer = await task
                tokens = int(solo_request_answer[1])
                answer = str(solo_request_answer[0])
                token_coast += tokens
                answers.append(answer)

                if len(answers) % 10 == 0:
                    await _update_progress(answers, chunks, message, msg)
                    await bot.send_chat_action(user_id, 'record_voice')

                if states.states.stop_gpt:
                    states.states.stop_gpt = False
                    await bot.send_chat_action(message.from_user.id, 'upload_audio')
                    await _handle_exception(answers, message)
                    await complete_audio_files(answers)
                    return [answers, token_coast]

            except CancelledError:
                logger.warning(f"Task {i} was cancelled.")
                break
            except Exception as e:
                logger.error(f"Error in task {i}: {e}")
                break

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await complete_audio_files(answers[0])
        return [answers, token_coast]

    await _update_progress(answers, chunks, message, msg)
    await _handle_exception(answers, message)
    await complete_audio_files(answers)
    return [answers, token_coast]


async def _update_progress(answers, chunks, message, msg):
    try:
        new_text = f'<b>Процесс работы:</b> <i>{len(answers)}/{len(chunks)}</i>'
        if msg.text != new_text:
            await bot.edit_message_text(new_text,
                                        chat_id=message.from_user.id,
                                        message_id=msg.message_id)
    except Exception as e:
        logger.error(f"Error updating progress: {e}")


async def complete_audio_files(files, input_folder="audio_files"):
    if not files:
        logger.error("No audio files generated.")
        return
    files =sorted([file for file in os.listdir('audio_files') if ('.mp3' in file and not('omnibot' in file))])
    if len(files) == 1:
        # Если только один файл, переименуем его в output.mp3
        single_file = files[0]
        output_file = os.path.join(input_folder, "output.mp3")
        os.rename(single_file, output_file)
        logger.info(f"Only one audio file generated, saved as {output_file}")
    else:
        # Если несколько файлов, объединяем их
        output_file = os.path.join(input_folder, "output.mp3")
        file_names = [os.path.basename(file) for file in files]
        sorted_mp3_files = sorted(file_names, key=lambda x: int(os.path.splitext(x)[0]))

        clips = [AudioFileClip(os.path.join(input_folder, file)) for file in sorted_mp3_files]

        if clips:
            final_clip = concatenate_audioclips(clips)
            final_clip.write_audiofile(output_file, codec="mp3")
            logger.info(f"Audio files concatenated and saved as {output_file}")
        else:
            logger.error("No valid audio clips found to concatenate.")


async def _handle_stop_gpt(answers, message):
    states.states.stop_gpt = False
    await _write_answers_to_file(answers, message)


async def _handle_exception(answers, message):
    await _write_answers_to_file(answers, message)


async def _write_answers_to_file(answers, message):
    filename = f"txt files/GPT{message.document.file_name.rsplit('.', 1)[0] + '.txt'}"
    async with aiofiles.open(filename, "w", encoding=TYPE_TXT_FILE or "utf-8") as file:
        for answer in answers or ['OmniBot']:
            await file.write(answer + "\n\n")
