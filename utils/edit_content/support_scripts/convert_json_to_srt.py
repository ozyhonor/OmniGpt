import os
import aiofiles
import json
import string
import nltk
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from utils.edit_content.create_translate import create_translate_text
import asyncio


def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation)).lower().strip()

nltk.download('punkt')


def format_time(seconds):
    millis = int((seconds % 1) * 1000)
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def split_sentence(text):
    text = text.replace("-", " ")

    words = text.split()
    finder = BigramCollocationFinder.from_words(words)
    scored = finder.score_ngrams(BigramAssocMeasures.likelihood_ratio)
    top_n = max(3, len(words) // 20)
    important_bigrams = {bigram for bigram, score in scored[:top_n]}

    min_size, max_size = 6, 9
    chunks = []
    temp_chunk = []

    for i, word in enumerate(words):
        temp_chunk.append(word)
        if i + 1 < len(words) and (words[i], words[i + 1]) in important_bigrams:
            continue
        if any(punctuation in word for punctuation in ",.!?;:") and len(temp_chunk) >= 3:
            chunks.append(temp_chunk)
            temp_chunk = []
        elif len(temp_chunk) >= max_size:
            chunks.append(temp_chunk)
            temp_chunk = []

    if temp_chunk:
        chunks.append(temp_chunk)

    final_chunks = []
    temp = []

    for chunk in chunks:
        if len(chunk) < 3:
            temp.extend(chunk)
        else:
            if temp:
                chunk = temp + chunk
                temp = []
            final_chunks.append(chunk)

    if temp:
        if final_chunks:
            final_chunks[-1].extend(temp)
        else:
            final_chunks.append(temp)

    return [" ".join(chunk) for chunk in final_chunks]


async def write_srt_file(chunks, filepath):
    async with aiofiles.open(filepath, mode='w') as file:
        for i, chunk in enumerate(chunks, start=1):
            start_time = chunk["start"]
            end_time = chunk["end"]
            text = chunk["text"]
            srt_entry = f"{i}\n{format_time(start_time)} --> {format_time(end_time)}\n{text}\n\n"
            await file.write(srt_entry)


async def json_to_srt(filepath: str, overlap: int = 0, translator: bool = False, dest_lang='en'):
    output_filepath = os.path.splitext(filepath)[0] + '.srt'
    output_filepath_translated = os.path.splitext(filepath)[0] + '_translated.srt'
    overlap = overlap / 1000

    async with aiofiles.open(filepath, mode='r') as file:
        content = await file.read()
        data = json.loads(content)
        words = data.get("words", [])
        sentences = split_sentence(data.get("text", ""))

    chunks = []
    translated_chunks = []
    sentence_index = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        current_sentence = []
        current_sentence_translated = []
        chunk_start_time = None
        chunk_end_time = None

        while sentence_index < len(words):
            word_data = words[sentence_index]
            word = word_data["word"]
            start_time = word_data["start"]
            end_time = word_data["end"]
            duration = int((end_time - start_time) * 100)
            formatted_word = f'{{\\k{duration}}}{word}'

            if chunk_start_time is None:
                chunk_start_time = start_time
            chunk_end_time = end_time

            current_sentence.append(formatted_word)
            current_sentence_translated.append(word)

            sentence_index += 1
            print(current_sentence_translated, sentence.strip())
            if remove_punctuation(" ".join(current_sentence_translated).strip()) == remove_punctuation(sentence.strip()):
                break

        if chunk_start_time is not None and chunk_end_time is not None:
            chunks.append({
                "start": chunk_start_time,
                "end": chunk_end_time + overlap,
                "text": " ".join(current_sentence)
            })

            translated_chunk_text = await create_translate_text(" ".join(current_sentence_translated), dest_lang)
            translated_chunks.append({
                "start": chunk_start_time,
                "end": chunk_end_time + overlap,
                "text": translated_chunk_text
            })

    await write_srt_file(chunks, output_filepath)
    await write_srt_file(translated_chunks, output_filepath_translated)
    return output_filepath
