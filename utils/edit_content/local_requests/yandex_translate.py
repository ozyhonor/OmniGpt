import srt
import asyncio
import aiohttp

import os
import datetime
from config_reader import yandex_api_key
from setup_logger import logger
import aiofiles

# Функция для перевода текста с использованием API Yandex
async def translate_text(text, target_language="ru"):
    URL = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {yandex_api_key}"
    }
    body = {
        "targetLanguageCode": target_language,
        "texts": [text]
    }


    # Отправка запроса на перевод
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, json=body, headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                print(response_data)
                return response_data['translations'][0]['text']

            else:
                logger.error(f"Error {response.status}: {await response.text()}")
                return None

# Функция для перевода субтитров
async def translate_subtitles(input_srt_path):
    base_name, ext = os.path.splitext(input_srt_path)
    output_srt_path = input_srt_path.replace('.srt', '_translated_ready.srt')

    logger.info(f"Translating subtitles for file: {input_srt_path}")

    # Чтение исходного файла с субтитрами
    async with aiofiles.open(input_srt_path, 'r', encoding='utf-8') as file:
        srt_content = await file.read()

    # Парсинг субтитров
    subtitles = list(srt.parse(srt_content))

    chunk = []
    chunk_text = ""
    max_chunk_size = 5000  # Максимальный размер текста для перевода
    new_subtitles = []

    # Процесс разделения и перевода блоков субтитров
    for subtitle in subtitles:
        subtitle_block = f"{subtitle.index}\n{subtitle.start} --> {subtitle.end}\n{subtitle.content}\n\n"
        if len(chunk_text) + len(subtitle_block) <= max_chunk_size:
            chunk.append(subtitle)
            chunk_text += subtitle_block
        else:
            # Переводим накопленный блок субтитров
            translated_chunk = await translate_chunk(chunk_text)
            new_subtitles.extend(apply_translations(chunk, translated_chunk))
            chunk = [subtitle]  # Начинаем новый блок
            chunk_text = subtitle_block

    # Перевод последнего блока
    if chunk:
        translated_chunk = await translate_chunk(chunk_text)
        new_subtitles.extend(apply_translations(chunk, translated_chunk))

    # Создаем новый SRT файл с переведенными субтитрами
    new_srt_content = srt.compose(new_subtitles)
    async with aiofiles.open(output_srt_path, 'w', encoding='utf-8') as output_file:
        await output_file.write(new_srt_content)

    logger.info(f"Translated subtitles saved to {output_srt_path}")
    return output_srt_path

# Функция перевода текста блоками
async def translate_chunk(chunk_text):
    logger.info(f"Translating chunk of size {len(chunk_text)} characters")
    translated_text = await translate_text(chunk_text)
    if translated_text is None:
        logger.error(f"Translation failed for chunk: {chunk_text[:100]}...")
    return translated_text

# Функция конвертации строки времени в timedelta
def convert_to_timedelta(time_str):
    hours, minutes, seconds = time_str.split(':')
    seconds_parts = seconds.replace(',', '.').split('.')

    seconds = int(seconds_parts[0])
    milliseconds = int(seconds_parts[1]) if len(seconds_parts > 1) else 0

    # Преобразование в timedelta с миллисекундами
    return datetime.timedelta(
        hours=int(hours),
        minutes=int(minutes),
        seconds=seconds,
        milliseconds=milliseconds
    )

# Функция для применения переведенного текста к исходным субтитрам
def apply_translations(chunk, translated_text):
    translated_blocks = translated_text.strip().split("\n\n")
    new_subtitles = []

    for i, subtitle in enumerate(chunk):
        # Проверка наличия соответствующего переведенного блока
        if i < len(translated_blocks):
            translated_content = translated_blocks[i].strip()
            lines = translated_content.split('\n')

            # Извлечение индекса субтитра
            try:
                index = subtitle.index
            except ValueError:
                logger.error(f"Invalid subtitle index at block {i}. Skipping.")
                continue

            # Используем исходные таймкоды
            start_time = subtitle.start
            end_time = subtitle.end

            # Объединение содержимого переведенного текста
            content = ' '.join(line.strip() for line in lines[2:]).strip()

            # Создание нового субтитра
            new_subtitle = srt.Subtitle(
                index=index,
                start=start_time,
                end=end_time,
                content=content
            )

            new_subtitles.append(new_subtitle)
        else:
            logger.warning(f"No translation available for subtitle {i + 1}.")

    return new_subtitles

