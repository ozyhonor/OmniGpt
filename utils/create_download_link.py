from config_reader import proxy_config
import aiohttp
import asyncio


import os
import asyncio
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from config_reader import service



def upload_file_sync(file_url: str):
    try:
        # Файл для загрузки
        file_metadata = {"name": os.path.basename(file_url)}
        media = MediaFileUpload(file_url, resumable=True)

        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        file_id = file.get("id")
        file_link = f"https://drive.google.com/file/d/{file_id}/view"

        service.permissions().create(
            fileId=file_id,
            body={"role": "reader", "type": "anyone"},
        ).execute()

        return file_link

    except HttpError as error:
        print(f"Произошла ошибка при загрузке файла: {error}")
        return None


async def upload_file_to_gDisk(file_url: str):
    file_link = await asyncio.to_thread(upload_file_sync, file_url)
    if file_link:
        return (f"{file_link}")
    else:
        print("❌ Произошла ошибка при загрузке файла.")





