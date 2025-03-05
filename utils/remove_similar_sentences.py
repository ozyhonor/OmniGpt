import re
import numpy as np
import aiofiles
import asyncio
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

# Инициализируем глобальные переменные
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

_russian_stopwords = None
_lemmatizer = WordNetLemmatizer()

def get_stopwords():
    """Загружает и кэширует стоп-слова для русского языка."""
    global _russian_stopwords
    if _russian_stopwords is None:
        _russian_stopwords = stopwords.words("russian")
    return _russian_stopwords

def lemmatize_text(text):
    """Лемматизирует текст с использованием NLTK."""
    words = nltk.word_tokenize(text)
    return ' '.join(_lemmatizer.lemmatize(word) for word in words)

def remove_punctuation(text):
    """Удаляет знаки препинания."""
    return re.sub(r'[^\w\s]', '', text)

def tokenize_and_remove_stopwords(text):
    """Токенизирует текст и удаляет стоп-слова."""
    stopwords_list = get_stopwords()
    tokens = text.split()
    filtered_tokens = [token for token in tokens if token.lower() not in stopwords_list]
    return ' '.join(filtered_tokens)

def preprocess_text(text):
    """Очищает текст: удаляет пунктуацию, лемматизирует, удаляет стоп-слова."""
    text = remove_punctuation(text)
    text = lemmatize_text(text)
    text = tokenize_and_remove_stopwords(text)
    print(text)
    return text

def preprocess_corpus(corpus):
    """Обрабатывает весь корпус синхронно."""
    return [preprocess_text(sentence) for sentence in corpus]

async def remove_similar_sentences(filename, threshold=0.18):
    """Читает файл, удаляет дублирующиеся предложения и сохраняет результат в два файла."""
    # Читаем файл асинхронно
    async with aiofiles.open(filename, 'r', encoding='UTF-8') as f:
        corpus = [line.strip() for line in await f.readlines() if line.strip()]

    # Обрабатываем текст (ТЕПЕРЬ СИНХРОННО)
    processed_corpus = preprocess_corpus(corpus)
    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform(processed_corpus)
    pairwise_similarity = (tfidf * tfidf.T).toarray()
    similar_pairs = []
    to_remove = set()
    for i in range(len(corpus)):
        for j in range(i + 1, len(corpus)):
            if pairwise_similarity[i, j] > threshold:
                to_remove.add(j)
                similar_pairs.append((corpus[i], corpus[j]))

    filtered_corpus = [sentence + '\n' for idx, sentence in enumerate(corpus) if idx not in to_remove]
    deleted_corpus = [sentence + '\n' for idx, sentence in enumerate(corpus) if idx in to_remove]

    # Записываем результат в файлы
    filtered_filename = f"{filename}".replace('txt files/', 'txt files/filtered_')
    deleted_filename = f"{filename}".replace('txt files/', 'txt files/deleted_')
    similar_pairs_filename = f"{filename}".replace('txt files/', 'txt files/paired_')

    async with aiofiles.open(filtered_filename, 'w', encoding='UTF-8') as f:
        await f.writelines(filtered_corpus)

    async with aiofiles.open(deleted_filename, 'w', encoding='UTF-8') as f:
        await f.writelines(deleted_corpus or 'omnigpt')

    async with aiofiles.open(similar_pairs_filename, 'w', encoding='UTF-8') as f:
        await f.write(f'omnigpt\n')
        for pair in similar_pairs:
            await f.write(f"Pair: {pair[0]} \n     {pair[1]}\n\n")

    return filtered_filename, deleted_filename, similar_pairs_filename

