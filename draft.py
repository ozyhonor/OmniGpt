import nltk
import string
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures

nltk.download('punkt')

def normalize(word):
    return word.strip(string.punctuation).lower()

def split_sentence(text):
    words = text.split()

    # 1. Определяем биграммы
    finder = BigramCollocationFinder.from_words(words)
    scored = finder.score_ngrams(BigramAssocMeasures.likelihood_ratio)

    # Выбираем топ-N биграмм, где N зависит от длины текста
    top_n = max(3, len(words) // 20)  # Минимум 3 биграммы, но не больше 10% от всех слов
    important_bigrams = {bigram for bigram, score in scored[:top_n]}

    # 2. Добавляем все биграммы, где первое слово — "the" или "The"
    for i in range(len(words) - 1):
        cleaned_word = words[i].strip(string.punctuation).lower()

        if cleaned_word == "the" or len(cleaned_word) == 1:
            important_bigrams.add((words[i], words[i + 1]))

    min_size, max_size = 6, 9
    chunks = []
    temp_chunk = []

    for i, word in enumerate(words):
        temp_chunk.append(word)

        # Проверяем, не является ли слово частью важной биграммы
        if i + 1 < len(words) and (words[i], words[i + 1]) in important_bigrams:
            continue  # Пропускаем разрыв, двигаемся дальше

        # Разрыв по знакам препинания, если длина фрагмента >= 3
        if any(punctuation in word for punctuation in ",.!?;:") and len(temp_chunk) >= 3:
            chunks.append(temp_chunk)
            temp_chunk = []
        # Разрыв по длине фрагмента
        elif len(temp_chunk) >= max_size:
            chunks.append(temp_chunk)
            temp_chunk = []

    if temp_chunk:
        chunks.append(temp_chunk)

    # Гарантируем, что минимум 3 слова в каждом фрагменте
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
    print(important_bigrams)

    return [" ".join(chunk) for chunk in final_chunks]

w1 = []
text = ' '.join(w1)

split_parts = split_sentence(text)

words_in_sentences = set(normalize(word) for sentence in split_parts for word in sentence.split())

all_words_present = all(normalize(word) in words_in_sentences for word in w1)

print(all_words_present)

print(split_parts)
