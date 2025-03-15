import aiofiles
import json
from utils.edit_content.create_translate import create_translate_text
import re
import os
from db.database import db

async def json_to_srt(filepath: str, overlap: int = 0, translator: bool = False, dest_lang='en'):
    # Формируем название выходного файла, заменяя расширение .json на .srt
    output_filepath = os.path.splitext(filepath)[0] + '.srt'
    output_filepath_translated = os.path.splitext(filepath)[0] + '_translated.srt'
    overlap = overlap / 1000

    # Чтение и обработка файла JSON
    async with aiofiles.open(filepath, mode='r') as file:
        content = await file.read()
        data = json.loads(content)
        words = data.get("words", [])
        text = re.split(r'\s+|[-]', data.get("text"))

    chunks = []
    translated_chunks = []
    current_chunk = []
    current_chunk_translated = []
    chunk_start_time = None
    chunk_end_time = None
    chunk_word_count = 0
    min_duration = 1.5  # Минимальная длина чанка в секундах

    max_gap = 3.0  # Максимальный разрыв между словами для установки конца чанка на start следующего слова

    for i, word_data in enumerate(words):
        if i >= len(text):
            break

        word = text[i]
        start_time = word_data["start"]
        end_time = word_data["end"]
        duration = int((end_time - start_time) * 100)
        translated_word = word
        word = f'{{\\k{duration}}}{word}'

        if chunk_start_time is None:
            chunk_start_time = start_time

        current_chunk.append(word)
        current_chunk_translated.append(translated_word)
        chunk_word_count += 1
        chunk_end_time = end_time

        next_word_start = words[i + 1]["start"] if i + 1 < len(words) else None

        if next_word_start is not None:
            next_chunk_end = next_word_start if (next_word_start - end_time) <= max_gap else end_time

            if end_time != next_word_start and chunk_word_count >= 3 and (
                    chunk_end_time - chunk_start_time) >= min_duration:
                chunks.append({
                    "start": chunk_start_time,
                    "end": next_chunk_end + overlap,
                    "text": " ".join(current_chunk)
                })
                translated_chunk_text = await create_translate_text(" ".join(current_chunk_translated), dest_lang)
                translated_chunks.append({
                    "start": chunk_start_time,
                    "end": next_chunk_end,
                    "text": translated_chunk_text
                })
                current_chunk = []
                current_chunk_translated = []
                chunk_start_time = None
                chunk_word_count = 0
            elif end_time == next_word_start and chunk_word_count >= 14:
                chunks.append({
                    "start": chunk_start_time,
                    "end": next_chunk_end + overlap,
                    "text": " ".join(current_chunk)
                })
                translated_chunk_text = await create_translate_text(" ".join(current_chunk_translated), dest_lang)
                translated_chunks.append({
                    "start": chunk_start_time,
                    "end": next_chunk_end,
                    "text": translated_chunk_text
                })
                current_chunk = []
                current_chunk_translated = []
                chunk_start_time = None
                chunk_word_count = 0

    if current_chunk:
        chunks.append({
            "start": chunk_start_time,
            "end": chunk_end_time,
            "text": " ".join(current_chunk)
        })
        translated_chunk_text = await create_translate_text(" ".join(current_chunk_translated), dest_lang)
        translated_chunks.append({
            "start": chunk_start_time,
            "end": chunk_end_time,
            "text": translated_chunk_text
        })

    await write_srt_file(chunks, output_filepath)
    await write_srt_file(translated_chunks, output_filepath_translated)
    return output_filepath

async def write_srt_file(chunks, output_filepath):
    async with aiofiles.open(output_filepath, mode='w') as file:
        for i, chunk in enumerate(chunks):
            start_time = format_srt_timestamp(chunk["start"])
            end_time = format_srt_timestamp(chunk["end"])
            text = chunk["text"]

            # Форматирование строки SRT
            srt_entry = f"{i + 1}\n{start_time} --> {end_time}\n{text}\n\n"
            await file.write(srt_entry)

def format_srt_timestamp(seconds_: float) -> str:
    hours, remainder = divmod(seconds_, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds % 1) * 1000)
    return f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}'
