import aiofiles
import json
import re
import os

async def json_to_srt(filepath: str, overlap: int = 0):
    # Формируем название выходного файла, заменяя расширение .json на .srt
    output_filepath = os.path.splitext(filepath)[0] + '.srt'

    # Чтение и обработка файла JSON
    async with aiofiles.open(filepath, mode='r') as file:
        content = await file.read()
        data = json.loads(content)
        words = data.get("words", [])
        text = re.split(r'\s+|[-]',data.get("text"))
        print(len(words), len(text))
        for _ in range(len(text)):
            print(words[_], text[_])
        chunks = []
        current_chunk = []
        chunk_start_time = None
        chunk_end_time = None
        chunk_word_count = 0

        for i, word_data in enumerate(words):
            if i > len(text)-1:
                break
            print(i)
            word = text[i]
            start_time = word_data["start"]
            end_time = word_data["end"]
            duration = int((word_data['end'] - word_data['start']) * 100)
            word = f'{{\\k{duration}}}{word}'

            if chunk_start_time is None:
                chunk_start_time = start_time

            current_chunk.append(word)
            chunk_word_count += 1
            chunk_end_time = end_time

            # Проверка на завершение чанка по условиям
            if (re.search(r'[,.!?]', word) and chunk_word_count >= 3) or chunk_word_count == 5:
                chunks.append({
                    "start": chunk_start_time,
                    "end": chunk_end_time + overlap,
                    "text": " ".join(current_chunk)
                })
                # Сброс текущего чанка
                current_chunk = []
                chunk_start_time = None
                chunk_word_count = 0

        # Добавляем последний чанк, если остался текст
        if current_chunk:
            chunks.append({
                "start": chunk_start_time,
                "end": chunk_end_time,
                "text": " ".join(current_chunk)
            })

    # Запись SRT файла
    await write_srt_file(chunks, output_filepath)

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
