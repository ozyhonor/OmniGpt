import asyncio
import aiohttp
import numpy as np
import config_reader
import random
import re
# import nltk
from nltk.corpus import stopwords


# Загрузка данных stopwords
# nltk.download('stopwords')
stop_words = set(stopwords.words('russian'))  # Стоп-слова русского языка

p = config_reader.proxy_config()['http']
print(p)
API_KEY = random.choice(config_reader.gpt_tokens)
API_URL = 'https://api.openai.com/v1/embeddings'


def normalize_text(text):
    """Нормализует текст: удаляет пунктуацию, приводит в нижний регистр, токенизирует и убирает стоп-слова."""
    # Удаляем лишние символы
    text = re.sub(r'[^\w\s\(\)\{\}\[\]\\=\+\-\*/^%.,]', '', text)
    # Приводим к нижнему регистру
    text = text.lower()
    # Простая токенизация с использованием регулярных выражений
    words = re.findall(r'\b\w+\b', text)  # Находит все слова
    # Убираем стоп-слова
    filtered_words = [word for word in words if word not in stop_words]
    # Возвращаем нормализованный текст
    return ' '.join(filtered_words)


def preprocess_file(file_path):
    """Читает файл, разбивает на строки и нормализует текст."""
    with open(file_path, 'r') as f:
        text = f.read()

    # Разделяем текст на строки
    sentences = re.split(r'\n+', text)

    # Убираем пустые строки и нормализуем текст
    sentences = [normalize_text(sentence) for sentence in sentences if sentence.strip()]
    return sentences


async def get_embedding(session, text):
    """Запрашивает эмбеддинг текста через API OpenAI."""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'text-embedding-ada-002',
        'input': text
    }

    async with session.post(API_URL, headers=headers, json=data, proxy=p, ssl=False) as response:
        response_data = await response.json()
        return response_data['data'][0]['embedding']


def cosine_similarity(vec1, vec2):
    """Вычисляет косинусное сходство между двумя векторами."""
    dot_product = np.dot(vec1, vec2)
    norm_a = np.linalg.norm(vec1)
    norm_b = np.linalg.norm(vec2)
    return dot_product / (norm_a * norm_b)


async def main(sentences):
    """Вычисляет эмбеддинги и сортирует предложения по среднему косинусному сходству."""
    async with aiohttp.ClientSession() as session:
        # Получаем эмбеддинги
        embeddings = await asyncio.gather(*(get_embedding(session, sentence) for sentence in sentences))

    # Подсчитываем матрицу сходств
    n = len(embeddings)
    similarity_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            similarity_matrix[i, j] = sim
            similarity_matrix[j, i] = sim

    # Считаем среднее сходство для каждого предложения
    similarities = []
    for i in range(n):
        avg_similarity = np.mean(similarity_matrix[i])
        similarities.append((sentences[i], avg_similarity))

    # Сортируем предложения по среднему сходству
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities


if __name__ == '__main__':
    # Шаг 1. Предобработка
    file_path = 'Тест для ии сортирова.txt'
    sentences = preprocess_file(file_path)

    # Шаг 2. Вычисляем и сортируем
    results = asyncio.run(main(sentences))

    # Шаг 3. Сохраняем отсортированный текст
    with open('sorted_sentences.txt', 'w') as f:
        for sentence, score in results:
            f.write(f"{sentence}\n")

    print("Сортировка завершена. Результаты сохранены в 'sorted_sentences.txt'.")
