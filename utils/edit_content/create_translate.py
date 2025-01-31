import aiohttp
import asyncio
from googletrans import Translator
from config_reader import proxy_config

async def create_translate_text(text, dest='en'):
    proxy = proxy_config()

    async with aiohttp.ClientSession() as session:

        session.proxies = proxy

        translator = Translator()

        max_attempts = 3
        attempt = 0
        while attempt < max_attempts:
            try:
                result = await translator.translate(text, dest=dest)
                print(dest)
                translated_text = result.text
                print(translated_text)
                return translated_text
            except Exception as e:
                print(f"Attempt {attempt+1} failed with error: {e}")
                attempt += 1
                continue

        print("Translation failed after 3 attempts.")
        return ' '