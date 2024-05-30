import requests
from random import choice
from config_reader import gpt_tokens, proxy_config


def send_recognize_request(file, smart = False):
    if smart:
        format = '.srt'
        data = {'model': 'whisper-1',
                'response_format': 'srt'}
    else:
        format = '.json'
        data = {'model': 'whisper-1',
            'response_format': 'verbose_json',
            'timestamp_granularities[]': 'word'}
    api_key = choice(gpt_tokens)

    url = 'https://api.openai.com/v1/audio/transcriptions'
    headers = {'Authorization': f'Bearer {api_key}'}
    files = {'file': open(f'{file}', 'rb')}
    response = requests.post(url, headers=headers, data=data, files=files, proxies=proxy_config())
    print(response)
    with open(f'{file.replace(".mp3", format)}', 'w', encoding='utf-8') as f:
        f.write(response.text)