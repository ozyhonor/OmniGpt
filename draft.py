from googletrans import Translator
import requests
from config_reader import proxy_config


def create_translate_text(text, dest='ru'):

    proxy = proxy_config()
    requests.Session().proxies.update(proxy)
    translator = Translator()
    result = translator.translate(f'{text}', dest=dest)
    translated_text = result.text
    return translated_text

