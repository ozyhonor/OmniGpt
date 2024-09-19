import asyncio
import json
import os
import pysubs2
from setup_logger import logger
from db.database import db
from utils.edit_content.create_translate import create_translate_text
from typing import List, Dict, Tuple
import json
import pysubs2
from typing import List, Dict
import os
from setup_logger import logger

import json
import pysubs2
from typing import List, Dict
import os
from setup_logger import logger

async def configure_style(user_id: int) -> pysubs2.SSAStyle:
    # Получение пользовательских настроек для стилей субтитров
    primary_color = await db.get_user_setting('primary_color', user_id)
    primary_r, primary_g, primary_b, primary_a = map(int, primary_color.split(','))

    second_color = await db.get_user_setting('second_color', user_id)
    second_r, second_g, second_b, second_a = map(int, second_color.split(','))

    outline_color = await db.get_user_setting('outline_color', user_id)
    outline_r, outline_g, outline_b, outline_a = map(int, outline_color.split(','))

    background_color = await db.get_user_setting('background_color', user_id)
    background_r, background_g, background_b, background_a = map(int, background_color.split(','))

    style = pysubs2.SSAStyle()
    style.fontname = await db.get_user_setting('font', user_id)
    style.fontsize = await db.get_user_setting('font_size', user_id)
    style.primarycolor = pysubs2.Color(primary_r, primary_g, primary_b, primary_a)
    style.secondarycolor = pysubs2.Color(second_r, second_g, second_b, second_a)
    style.outlinecolor = pysubs2.Color(outline_r, outline_g, outline_b, outline_a)
    style.backcolor = pysubs2.Color(background_r, background_g, background_b, background_a)
    style.outline = await db.get_user_setting('outline_size', user_id)
    style.alignment = pysubs2.Alignment.BOTTOM_CENTER

    return style


async def json_to_ass(json_file: str, user_id: int, max_time_gap: float = 2.0) -> str:
    base_name = os.path.splitext(json_file)[0]
    output_subtitles = f'{base_name}.ass'

    # Загрузка данных из JSON файла
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    words = data['words']
    max_words = await db.get_user_setting('max_words', user_id)

    # Создаем новый объект субтитров
    subs = pysubs2.SSAFile()

    # Настройка стилей субтитров
    style = await configure_style(user_id)
    subs.styles["Default"] = style

    # Генерация субтитров с эффектом караоке
    chunks = split_words_into_chunks(words, max_words, max_time_gap)

    # Генерация событий для ASS файла
    for chunk in chunks:
        start_time, end_time = get_chunk_time(chunk)
        chunk_text, trans_text = generate_karaoke_text(chunk)

        event = pysubs2.SSAEvent(
            start=start_time * 1000,
            end=end_time * 1000,
            text=f'{{\\b1}}{chunk_text}{{\\b0}}\n{trans_text}'
        )
        subs.events.append(event)

    # Сохранение результата в файл .ass
    subs.save(output_subtitles)
    return output_subtitles


def split_words_into_chunks(words: List[Dict[str, float]], max_words_per_chunk: int, max_time_gap: float) -> List[
    List[Dict[str, float]]]:
    chunks = []
    current_chunk = []

    for i, word in enumerate(words):
        if len(current_chunk) < max_words_per_chunk and (
                not current_chunk or word['start'] - current_chunk[-1]['end'] <= max_time_gap):
            current_chunk.append(word)
        else:
            chunks.append(current_chunk)
            current_chunk = [word]

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def get_chunk_time(chunk: List[Dict[str, float]]) -> Tuple[float, float]:
    start_time = chunk[0]['start']
    end_time = chunk[-1]['end']
    return start_time, end_time


def generate_karaoke_text(chunk: List[Dict[str, float]]) -> Tuple[str, str]:
    chunk_text = ""
    trans_text = ""

    for word_data in chunk:
        word_duration = int((word_data['end'] - word_data['start']) * 100)
        word_text = word_data['word']
        word_trans = create_translate_text(word_text)  # Функция для перевода слова

        chunk_text += f"{{\\k{word_duration}}}{word_text} "
        trans_text += f"{word_trans} "

    return chunk_text.strip(), trans_text.strip()





