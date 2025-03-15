from random import choice
import asyncio
import traceback
import aiohttp
from config_reader import gpt_tokens, proxy_config
from setup_logger import logger
from time import time


async def create_solo_photo(text, size="1024x1024", count_of_pictures=1, model='dall-e-2',
                            max_retries=4):
    start_time = time()

    async def make_request(session, attempt, text):
        proxy = proxy_config().get('https')
        logger.info(f"Attempt {attempt} for image generation request.")

        api_key = choice(gpt_tokens)
        url = "https://api.openai.com/v1/images/generations"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Формируем запрос для DALL·E
        data = {
            "model": model,
            "prompt": f"{text}",
            "n": count_of_pictures,  # Сколько изображений нужно создать
            "size": size  # Размер изображения (например, '1024x1024' или '1792x1024')
        }

        try:
            async with session.post(url, json=data, headers=headers, proxy=proxy) as response:
                result = await response.json()
                status = response.status

                if status != 200:
                    logger.error(f"Request failed with status: {status}, response: {result}")
                    return None, '-'

                image_urls = [img_data['url'] for img_data in result.get('data', [])]  # Получаем URL изображений
                logger.info(f"Image generation successful: {image_urls}")
                return round(time() - start_time, 2), image_urls

        except Exception as e:
            logger.error(f"{traceback.format_exc()}")
            return None, '-'

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
        for attempt in range(1, max_retries + 1):
            time_taken, image_urls = await make_request(session, attempt, text)
            if image_urls != '-':
                return time_taken, image_urls
            logger.warning(f"Retrying... ({attempt}/{max_retries})")

    logger.error("Max retries reached. Image generation failed.")
    return None, '-'