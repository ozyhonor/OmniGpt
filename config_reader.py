import configparser

config = configparser.ConfigParser()
config.read('./keys.ini')

gpt_tokens = config.get('gpt', 'keys').split(',')
print(len(gpt_tokens), 'tokens')


def proxy_config():

    proxy_ips = config.get('proxy', 'ip').split(',')
    login = config.get('proxy', 'login')
    password = config.get('proxy', 'password')

    # Используем счетчик для отслеживания текущего индекса прокси
    if 'proxy_index' not in proxy_config.__dict__:
        proxy_config.proxy_index = 0
    else:
        proxy_config.proxy_index = (proxy_config.proxy_index + 1) % len(proxy_ips)

    current_proxy = proxy_ips[proxy_config.proxy_index]
    proxy_url = f'http://{login}:{password}@{current_proxy}'

    proxy_configuration = {
        'http': proxy_url,
        'https': proxy_url
    }

    return proxy_configuration

yt_mail_for_downloading = config.get('youtube_support_account', 'mail')
yt_pass_for_downloading = config.get('youtube_support_account', 'password')
po = config.get('youtube_support_account', 'po')

telegram_token = config.get('telegram', 'key')
admins_ids = config.get('telegram', 'admins_ids')
