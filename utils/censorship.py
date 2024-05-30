import re

def censorship(text):
    with open('bad_words.txt', encoding='utf-8') as f:
        bad_words = f.read().split('\n')
    for word in bad_words:
        pattern = r'\b{}\b'.format(re.escape(word))
        text = re.sub(pattern, '*' * len(word), text, flags=re.IGNORECASE)
    return text
