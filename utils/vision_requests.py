import aiohttp
import base64
from time import time
import logging
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


async def encode_image(image_path):
    return await asyncio.to_thread(_encode_image_sync, image_path)

def _encode_image_sync(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


async def vision_request(image_data, settings=None, model='gpt-4o', max_retries=4):
    start_time = time()

    async def make_request(session, attempt):
        proxy = proxy_config().get('https')  # Опционально, если требуется прокси
        logger.info(f"Attempt {attempt} for vision request.")
        api_key = choice(gpt_tokens)
        url = "https://api.openai.com/v1/chat/completions"

        # Кодируем изображение в base64
        base64_image = base64.b64encode(image_data).decode('utf-8')

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": f"{model}",
            "messages": [
                {
                    "role": "system",
                    "content": f"Ты — продвинутая модель для анализа изображений. Твоя задача — тщательно анализировать изображения и точно отвечать на запрос пользователя. Будь внимателен к деталям и строго следуй заданному вопросу, предоставь исчерпывающее описание содержимого изображения, избегая ненужных отклонений."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{settings or 'Что?'}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        try:
            async with session.post(url, headers=headers, json=payload, proxy=proxy) as response:
                status = response.status
                result = await response.json()

                if status != 200:
                    logger.error(f"Request failed with status: {status}")
                    return None, '', None

                answer = result['choices'][0]['message']['content']
                tokens_used = result['usage']['total_tokens']
                logger.info(f"Request successful: {tokens_used} tokens used.")
                return round(time() - start_time, 2), answer, tokens_used

        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            return None, '', None

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
        for attempt in range(1, max_retries + 1):
            time_taken, answer, tokens_used = await make_request(session, attempt)
            if answer:
                return time_taken, answer, tokens_used
            logger.warning(f"Retrying... ({attempt}/{max_retries})")

    logger.error("Max retries reached. Vision request failed.")
    return None, '', None