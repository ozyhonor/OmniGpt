import re


def split_text(text: str, model='gpt-3.5-turbo') -> list:

    if model == 'gpt-4':
        max_chunk_size = 35353
    elif model == 'gpt-4o':
        max_chunk_size = 35353
    elif model == 'gpt-4-turbo':
        max_chunk_size = 35353
    elif model == 'gpt-4o-mini':
        max_chunk_size = 35353
    else:  # По умолчанию gpt-3.5-turbo
        max_chunk_size = 4444

    pattern = re.compile(r'(?<=[\n.!?])')
    sentences = pattern.split(text)
    current_chunk = ''
    chunks = []

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
