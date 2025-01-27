import aiohttp
import asyncio
from googletrans import Translator
from config_reader import proxy_config

async def create_translate_text(text, dest='ru'):
    proxy = proxy_config()

    async with aiohttp.ClientSession() as session:

        session.proxies = proxy

        translator = Translator()

        max_attempts = 3
        attempt = 0
        while attempt < max_attempts:
            try:
                # Здесь предполагается, что translator.translate возвращает корутину
                result = await translator.translate(text, dest=dest)

                # Если 'result' поддерживает асинхронные свойства
                if asyncio.iscoroutine(result.text):
                    translated_text = await result.text
                else:
                    translated_text = result.text

                return translated_text
            except Exception as e:
                print(f"Attempt {attempt+1} failed with error: {e}")
                attempt += 1
                continue

        print("Translation failed after 3 attempts.")
        return ' '