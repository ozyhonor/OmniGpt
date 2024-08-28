import json
from typing import List, Dict
import os
from setup_logger import logger


def json_to_srt(json_file: str, words_per_chunk: int, overlap: int):

    base_name = os.path.splitext(json_file)[0]
    output_subtitles = f'{base_name}.srt'

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    text = data['text']
    words = data['words']

    chunks = split_text_into_chunks(text, words, words_per_chunk)
    srt_content = generate_srt_content(chunks, words, overlap=overlap)

    with open(output_subtitles, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    logger.info(f'File success converting json to srt with filename {output_subtitles}')
    return output_subtitles

def split_text_into_chunks(text: str, words: List[Dict[str, float]], words_per_chunk: int) -> List[tuple[str, int, int]]:
    chunks = []
    current_chunk = []
    current_chunk_text = ''
    start_index = 0

    last_word_end = words[-1]['end']

    for i, word in enumerate(words):
        current_chunk.append(word['word'])
        current_chunk_text += ' ' + word['word']

        if len(current_chunk) >= words_per_chunk or word['end'] >= last_word_end:
            chunks.append((current_chunk_text.strip(), start_index, i))
            current_chunk = []
            current_chunk_text = ''
            start_index = i + 1

    return chunks

def generate_srt_content(chunks: List[tuple[str, int, int]], words: List[Dict[str, float]], overlap:int) -> str:
    srt_content = ''
    index = 1

    for chunk, start_index, end_index in chunks:
        if end_index < len(words) - 1:
            start_time, end_time = get_chunk_time(start_index, end_index, words)
            srt_content += f'{index}\n'
            srt_content += f'{format_time(start_time)} --> {format_time(end_time+overlap/1000)}\n'
            srt_content += f'{chunk}\n\n'
            index += 1

    return srt_content
def get_chunk_time(start_index: int, end_index: int, words: List[Dict[str, float]]) -> tuple[float, float]:
    start_time = words[start_index]['start']
    end_time = words[end_index]['end']
    print(start_time, end_time)
    return start_time, end_time

def format_time(time: float) -> str:
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds % 1) * 1000)

    return f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}'

