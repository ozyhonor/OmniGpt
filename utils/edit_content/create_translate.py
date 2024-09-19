import aiohttp
import asyncio
from googletrans import Translator
from config_reader import proxy_config

async def create_translate_text(text, dest='ru'):
    proxy = proxy_config()

    # Настройка прокси для aiohttp
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Обновление прокси для сессии
        session.proxies = proxy

        translator = Translator()

        max_attempts = 3
        attempt = 0
        while attempt < max_attempts:
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, translator.translate, text, dest)
                translated_text = result.text
                return translated_text
            except Exception as e:
                print(f"Attempt {attempt+1} failed with error: {e}")
                attempt += 1
                continue

        print("Translation failed after 3 attempts.")
        return ' '