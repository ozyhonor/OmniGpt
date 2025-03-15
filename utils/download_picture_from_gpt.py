import aiohttp
import asyncio
import os
from urllib.parse import urlparse, unquote
from utils.checkUrl import check_url


async def download_image(url, folder="images"):
    """Скачивает изображение по URL и сохраняет его в указанную папку."""
    os.makedirs(folder, exist_ok=True)  # Создаём папку, если её нет

    # Парсим URL, чтобы извлечь имя файла
    parsed_url = urlparse(url)
    filename = os.path.join(folder, os.path.basename(parsed_url.path))  # Получаем название файла без параметров
    filename = unquote(filename)  # Декодируем URL-encoded строку

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(filename, "wb") as f:
                    f.write(await response.read())
                print(f"Изображение сохранено: {filename}")
                return filename  # Возвращаем путь к файлу
            else:
                print(f"Ошибка загрузки {url}: {response.status}")
                return None  # Возвращаем None в случае ошибки


async def download_images(urls):
    tasks = [download_image(url) for url in urls if check_url(url)]
    results = await asyncio.gather(*tasks)
    return [file for file in results if file]  # Возвращаем список успешно скачанных файлов
