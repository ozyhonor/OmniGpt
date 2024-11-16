import re


def split_text(text: str, token) -> list:

    pattern = re.compile(r'(?<=[\n.!?])')
    sentences = pattern.split(text)
    current_chunk = ''
    chunks = []

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < token:
            current_chunk += sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
