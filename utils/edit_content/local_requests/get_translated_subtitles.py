import srt
import asyncio
from utils.edit_content.create_translate import create_translate_text
import os
from setup_logger import logger


async def translate_subtitles(input_srt_path):
    # Получение базового имени файла и его расширения
    base_name, ext = os.path.splitext(input_srt_path)

    # Создание нового имени файла с суффиксом "_translated"
    output_srt_path = f"{base_name}_translated{ext}"

    logger.info(f"Translating subtitles for file: {input_srt_path}")

    # Чтение содержимого исходного файла субтитров
    with open(input_srt_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()

    # Парсинг SRT контента
    subtitles = list(srt.parse(srt_content))

    # Создание списка для новых субтитров
    new_subtitles = []

    # Асинхронный перевод каждого чанка
    for subtitle in subtitles:
        original_text = subtitle.content
        translated_text = await create_translate_text(original_text)

        # Форматирование нового контента: оригинальный текст + перевод
        new_content = f"{original_text}\n{translated_text}"

        # Создание нового объекта субтитра с теми же временными метками, но новым контентом
        new_subtitle = srt.Subtitle(
            index=subtitle.index,
            start=subtitle.start,
            end=subtitle.end,
            content=new_content
        )

        new_subtitles.append(new_subtitle)

    # Композиция нового SRT файла
    new_srt_content = srt.compose(new_subtitles)

    # Запись нового SRT файла
    with open(output_srt_path, 'w', encoding='utf-8') as output_file:
        output_file.write(new_srt_content)

    logger.info(f"Translated subtitles saved to {output_srt_path}")

    # Возвращаем путь к новому файлу
    return output_srt_path
