import re

dict_bool = {'✅': 1, '❌': 0}

video_stamps = 'Пожалуйста, введите временные метки для нарезки видео в формате примера: 1:21-3:54. Если временная метка превышает один час, пожалуйста, укажите ее в формате 66:21-72:48.'

ideal_settings = '''
Ты очень умная и полезная модель, придерживайся следующих правил!
1)Тебе подается только отрывки файлов субтитров такого формата:
00:43->00:46
-Is it deep? -No, it's a little
00:46->00:49
rhere is a stair and then it goes up again
00:49->00:52
2)Тебе нужно складывать такие временные метки в 1 временную метку, чтоб получался временной код СТРОГО до минуты времени. Обязательно придерживайся формата вывода ответов и соблюдай условие, что времянная метка должна быть до минуты времени СТРОГО 
3)После того, как ты создал такую новую времянную метку, тебе нужно ее назвать от лица автора тик ток канала или автора Youtube Shorts (Пожалуйста не называй и не пиши плохие, оскорбительные или другие не приятные слова) добавить соответствующие теги, смайлики при желании для этого времянного отрезка. То-есть тебе нужно складывать временные метки осознанно, чтоб была тема ролика, который будет создаваться по этим временным меткам.
4)Формат ответа:
начало-конец
название, теги тд. тп
'''


youtube_download_settings = ('<b>Скачать с Youtube:</b>'
                             '<blockquote><b>Субтитры  txt:  </b>{0}</blockquote>\n'
                             '<blockquote><b>Видео  mp4:  </b>{1}</blockquote>\n'
                             '<blockquote><b>Аудио  mp3:  </b>{2}</blockquote>\n'
                             '<blockquote><b>Язык субтитров:  </b>{3}</blockquote>')

wait_youtube_link = '<b>Ожидается ссылка на ютуб контент</b>'
wait_youtube_playlist_link = '<b>Ожидается ссылка на ютуб плейлист</b>'


video_settings_message = (
'''
Ваши настройки
Разрешение: {resolution}
Добавить субтитры: {subtitles}
Шрифт: {font}
Размер: {size}
Цвет: {color}
Доп цвет: {second_color}
Цвет перевода: {translated_color}
Максимум слов: {max_words}
Позиция: {position}
Добавить обводку субтитрам: {outline}
Размер обводки: {outline_size}
Цвет обводки: {outline_color}
Добавить тень субтитрам: {shadow}
Цвет тени: {shadow_color}
Добавить переводчик: {translator}
Язык перевода: {translated_language}
Скорость оригинала: {original_speed}
Скорость перевода: {translation_speed}
Нахлёст: {overlap}
Умные субтитры: {smart_sub}
Нарезать видео: {timestamps}
Интересные моменты: {intrested_moment}
'''
)

translator_text_panel = '<b><blockquote>Перевести на {0} {1}</blockquote></b>\n<b><blockquote>{2}/5</blockquote></b>'

write_gpt_settings = """
<b>Введите настройки запроса</b>
"""

ideal_video_settings ="""Тебе подаются отрывки текста, каждый отрывок с новой строки, всего отрывков {отрывки}.
Тебе нужно:1) Перевести эти отрывки на русский язык
2)Соблюдать структуру отрывков, твой ответ обязательно должен содержать {отрывки} переводов, не больше не меньше. Если ответ содержит другое колличество переводов - ответ считается не действительным. 
Перед отправкой проверь, что твой ответ содержит ровно {отрывки} отрывков и все они переведенны на русский язык"""

settings_sample_pattern = {
    'resolution': re.compile(r'Разрешение:\s*((\d+x\d+)|(Original|original))'),
    'subtitles': re.compile(r'Добавить субтитры:\s*(✅|❌|1|0)'),
    'font': re.compile(r'Шрифт:\s*(.+)'),
    'translated_color': re.compile(r'Шрифт:\s*(.+)'),
    'font_size': re.compile(r'Размер:\s*(\d+)'),
    'second_color': re.compile(r'Доп цвет:\s*(\d{1,3},\d{1,3},\d{1,3},\d{1,3})'),
    'primary_color': re.compile(r'Цвет:\s*(\d{1,3},\d{1,3},\d{1,3},\d{1,3})'),
    'max_words': re.compile(r'Максимум слов:\s*(\d+)'),
    'position': re.compile(r'Позиция:\s*(\w+)'),
    'outline': re.compile(r'Добавить обводку субтитрам:\s*(✅|❌|1|0)'),
    'outline_size': re.compile(r'Размер обводки:\s*(\d+)'),
    'outline_color': re.compile(r'Цвет обводки:\s*(\d{1,3},\d{1,3},\d{1,3},\d{1,3})'),
    'background': re.compile(r'Добавить тень субтитрам:\s*(✅|❌|1|0)'),
    'shadow_color': re.compile(r'Цвет тени:\s*(\d{1,3},\d{1,3},\d{1,3},\d{1,3})'),
    'translator': re.compile(r'Добавить переводчик:\s*(✅|❌|1|0)'),
    'translated_language': re.compile(r'Язык перевода:\s*(\w+)'),
    'original_speed': re.compile(r'Скорость оригинала:\s*([\d.]+)'),
    'translation_speed': re.compile(r'Скорость перевода:\s*([\d.]+)'),
    'overlap': re.compile(r'Нахлёст:\s*(\d+)'),
    'smart_sub': re.compile(r'Умные субтитры:\s*(✅|❌|1|0)'),
    'timestamps': re.compile(r'Нарезать видео:\s*(\d+)')
}


default_settings_gpt = """
Анализируй текст на предмет голословных утверждений.
Ищи попытки ввести в заблуждение или манипуляции.
Обращай внимание на неграмотные утверждения и ошибки.
Идентифицируй элементы пропаганды и необоснованные утверждения.
Определяй бессмысленные выражения, которые добавляют эмоциональную окраску.
Познакомься с контекстом, в котором автор может ошибаться.
Будь бдителен к попыткам ввести в заблуждение и подтасовыванию фактов.
Опознавай подмену понятий и использование неоднозначных терминов.

Следуй этой инструкции, чтобы обнаруживать указанные элементы и анализировать текст более точно.
"""

future_request_information = """
➖➖➖<b>{}</b>➖➖➖
"""

synthesis_information = """
<b>Настройки запроса</b>\n<blockquote><b>Скорость</b>: <i>{0}</i></blockquote>\n<blockquote><b>Голос:</b> <i>{1}</i></blockquote>
"""
synthesis_rate_info = '''
<b>Скорость генерируемого звука. Напишите значение от 0,25 до 4,0. 1.0 является значением по умолчанию.</b>
'''


synthesis_voice_info = '''
<b>Голос, который будет использоваться при создании звука. Выберите вариант из списка.</b>
'''


settings_speechkit = """
<b>Настройки запроса</b>: <i>Озвучить текст</i>\n<b>Скорость:</b> <i>{0}</i>\n<b>Пол:</b><i>{1}</i>\n<b>Сервис:</b><i>{2}</i>
"""

rate_edel = """
<b>Введите число в диапазоне [1:2]</b>
"""

languages = [
        {'code': 'af', 'flag': '🇿🇦', 'name': 'Afrikaans'},
        {'code': 'ar', 'flag': '🇸🇦', 'name': 'Arabic'},
        {'code': 'hy', 'flag': '🇦🇲', 'name': 'Armenian'},
        {'code': 'az', 'flag': '🇦🇿', 'name': 'Azerbaijani'},
        {'code': 'be', 'flag': '🇧🇾', 'name': 'Belarusian'},
        {'code': 'bs', 'flag': '🇧🇦', 'name': 'Bosnian'},
        {'code': 'bg', 'flag': '🇧🇬', 'name': 'Bulgarian'},
        {'code': 'ca', 'flag': '🇪🇸', 'name': 'Catalan'},
        {'code': 'zh-cn', 'flag': '🇨🇳', 'name': 'Chinese (Simplified)'},
        {'code': 'hr', 'flag': '🇭🇷', 'name': 'Croatian'},
        {'code': 'cs', 'flag': '🇨🇿', 'name': 'Czech'},
        {'code': 'da', 'flag': '🇩🇰', 'name': 'Danish'},
        {'code': 'nl', 'flag': '🇳🇱', 'name': 'Dutch'},
        {'code': 'en', 'flag': '🇬🇧', 'name': 'English'},
        {'code': 'et', 'flag': '🇪🇪', 'name': 'Estonian'},
        {'code': 'fi', 'flag': '🇫🇮', 'name': 'Finnish'},
        {'code': 'fr', 'flag': '🇫🇷', 'name': 'French'},
        {'code': 'gl', 'flag': '🇪🇸', 'name': 'Galician'},
        {'code': 'de', 'flag': '🇩🇪', 'name': 'German'},
        {'code': 'el', 'flag': '🇬🇷', 'name': 'Greek'},
        {'code': 'he', 'flag': '🇮🇱', 'name': 'Hebrew'},
        {'code': 'hi', 'flag': '🇮🇳', 'name': 'Hindi'},
        {'code': 'hu', 'flag': '🇭🇺', 'name': 'Hungarian'},
        {'code': 'is', 'flag': '🇮🇸', 'name': 'Icelandic'},
        {'code': 'id', 'flag': '🇮🇩', 'name': 'Indonesian'},
        {'code': 'it', 'flag': '🇮🇹', 'name': 'Italian'},
        {'code': 'ja', 'flag': '🇯🇵', 'name': 'Japanese'},
        {'code': 'kn', 'flag': '🇮🇳', 'name': 'Kannada'},
        {'code': 'kk', 'flag': '🇰🇿', 'name': 'Kazakh'},
        {'code': 'ko', 'flag': '🇰🇷', 'name': 'Korean'},
        {'code': 'lv', 'flag': '🇱🇻', 'name': 'Latvian'},
        {'code': 'lt', 'flag': '🇱🇹', 'name': 'Lithuanian'},
        {'code': 'mk', 'flag': '🇲🇰', 'name': 'Macedonian'},
        {'code': 'ms', 'flag': '🇲🇾', 'name': 'Malay'},
        {'code': 'mr', 'flag': '🇮🇳', 'name': 'Marathi'},
        {'code': 'mi', 'flag': '🇳🇿', 'name': 'Maori'},
        {'code': 'ne', 'flag': '🇳🇵', 'name': 'Nepali'},
        {'code': 'no', 'flag': '🇳🇴', 'name': 'Norwegian'},
        {'code': 'fa', 'flag': '🇮🇷', 'name': 'Persian'},
        {'code': 'pl', 'flag': '🇵🇱', 'name': 'Polish'},
        {'code': 'pt', 'flag': '🇵🇹', 'name': 'Portuguese'},
        {'code': 'ro', 'flag': '🇷🇴', 'name': 'Romanian'},
        {'code': 'ru', 'flag': '🇷🇺', 'name': 'Russian'},
        {'code': 'sr', 'flag': '🇷🇸', 'name': 'Serbian'},
        {'code': 'sk', 'flag': '🇸🇰', 'name': 'Slovak'},
        {'code': 'sl', 'flag': '🇸🇮', 'name': 'Slovenian'},
        {'code': 'es', 'flag': '🇪🇸', 'name': 'Spanish'},
        {'code': 'sw', 'flag': '🇰🇪', 'name': 'Swahili'},
        {'code': 'sv', 'flag': '🇸🇪', 'name': 'Swedish'},
        {'code': 'tl', 'flag': '🇵🇭', 'name': 'Tagalog'},
        {'code': 'ta', 'flag': '🇮🇳', 'name': 'Tamil'},
        {'code': 'th', 'flag': '🇹🇭', 'name': 'Thai'},
        {'code': 'tr', 'flag': '🇹🇷', 'name': 'Turkish'},
        {'code': 'uk', 'flag': '🇺🇦', 'name': 'Ukrainian'},
        {'code': 'ur', 'flag': '🇵🇰', 'name': 'Urdu'},
        {'code': 'vi', 'flag': '🇻🇳', 'name': 'Vietnamese'},
        {'code': 'cy', 'flag': '🏴', 'name': 'Welsh'},
    ]

settings_request = """
<b>Настройки запроса</b>:\n<pre><i>{0}</i></pre><i></i>\n\n<blockquote>🌡 <i>{1}</i></blockquote>\n<blockquote><i>🤖 {2}</i></blockquote>\n<blockquote><i>📏 {3}</i></blockquote>
"""

vision_request = """
<b>Настройки запроса</b>:\n<pre><i>{0}</i></pre><i></i>\n\n<blockquote><i>🤖 {1}</i></blockquote>
"""



water_mark_omnigpt = """
➖➖➖<b>OmniGpt</b>➖➖➖
<b>Токенов:</b> <i>{0} потрачено</i> 
"""
