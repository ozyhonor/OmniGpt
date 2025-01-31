import os
import asyncio
import time

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError


SERVICE_ACCOUNT_FILE = "client_secrets.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build("drive", "v3", credentials=creds)

# Функция для загрузки файла
def upload_file_sync(file_url: str):
    try:
        # Файл для загрузки
        file_metadata = {"name": os.path.basename(file_url)}
        media = MediaFileUpload(file_url, resumable=True)

        # Загружаем файл
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        file_id = file.get("id")
        file_link = f"https://drive.google.com/file/d/{file_id}/view"

        # Устанавливаем разрешение на публичный доступ
        service.permissions().create(
            fileId=file_id,
            body={"role": "reader", "type": "anyone"},
        ).execute()

        return file_link

    except HttpError as error:
        print(f"Произошла ошибка при загрузке файла: {error}")
        return None

# Асинхронная обертка для запуска синхронной функции в другом потоке
async def upload_file(file_url: str):
    # Запускаем синхронную функцию в другом потоке
    file_link = await asyncio.to_thread(upload_file_sync, file_url)
    if file_link:
        print(f"✅ Файл успешно загружен! Вот ссылка: {file_link}")
    else:
        print("❌ Произошла ошибка при загрузке файла.")


# Пример асинхронного вызова функции
async def main():
    file_url = "audio/output.mp3"  # Пример пути к файлу
    await upload_file(file_url)

# Запуск асинхронной программы
if __name__ == "__main__":
    asyncio.run(main())
