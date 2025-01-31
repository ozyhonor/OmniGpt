from config_reader import proxy_config
import aiohttp
import asyncio


async def upload_to_gofileio(file_path):
    url = "https://api.gofile.io/uploadFile"  # API GoFile
    proxy = proxy_config().get('https')  # Ваша функция для получения прокси, если используется
    timeout = aiohttp.ClientTimeout(total=2000)

    # Открываем файл асинхронно
    async with aiohttp.ClientSession(timeout=timeout) as session:
        with open(file_path, 'rb') as f:
            # Формируем запрос
            files = {'file': f}

            async with session.post(url, data=files, proxy=proxy) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get("status") == "ok":
                        return response_data["data"]["downloadPage"]  # Ссылка на скачивание
                    else:
                        print(f"Error from GoFile: {response_data}")
                        return None
                else:
                    print(f"HTTP Error: {response.status}")
                    return None

