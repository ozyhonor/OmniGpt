import requests
from config_reader import gpt_tokens
from random import choice
from config_reader import proxy_config


def send_request_to_embedding(text):
    api_key = choice(gpt_tokens)

    url = 'https://api.openai.com/v1/embeddings'

    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {api_key}"}

    data = {"input": f"{text}",
            "model": "text-embedding-3-small"}

    response = requests.post(url, json=data, headers=headers, proxies=proxy_config())
    result = response.json()
    if response.status_code == 200:
        answer = result['choices'][0]['message']['content']
        print(answer)
        return answer
