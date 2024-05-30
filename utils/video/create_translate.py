from googletrans import Translator
import requests
from config_reader import proxy_config


def create_translate_text(text, dest='ru'):
    proxy = proxy_config()
    requests.Session().proxies.update(proxy)
    translator = Translator()

    max_attempts = 3
    attempt = 0
    while attempt < max_attempts:
        try:
            result = translator.translate(f'{text}', dest=dest)
            translated_text = result.text
            return translated_text
        except Exception as e:
            print(f"Attempt {attempt+1} failed with error: {e}")
            attempt += 1
            continue

    print("Translation failed after 3 attempts.")
    return ' '