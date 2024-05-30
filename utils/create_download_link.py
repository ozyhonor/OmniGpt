import requests
from config_reader import proxy_config

def upload_to_fileio(file_path):
    url = "https://file.io/"
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, files=files, proxies=proxy_config())
    
    if response.status_code == 200:
        file_info = response.json()
        return file_info['link']
    else:
        return None
