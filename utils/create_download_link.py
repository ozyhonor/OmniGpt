from config_reader import proxy_config
import aiohttp
import asyncio


async def upload_to_fileio(file_path):
    url = "https://file.io/"
    proxy = proxy_config().get('http')  # Ваша функция для получения прокси, если используется
    timeout = aiohttp.ClientTimeout(total=2000)
    # Открываем файл асинхронно
    async with aiohttp.ClientSession(trust_env=True, timeout=timeout) as session:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            # Отправка POST-запроса
            async with session.post(url, data=files, proxy=proxy, ssl=False) as response:
                if response.status == 200:
                    file_info = await response.json()
                    return file_info['link']
                else:
                    return None

