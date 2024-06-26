
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
                             '<blockquote><b>Субтитры  txt:  </b>{0}</blockquote>'
                             '<blockquote><b>Видео  mp4:  </b>{1}</blockquote>'
                             '<blockquote><b>Аудио  mp3:  </b>{2}</blockquote>')

wait_youtube_link = '<b>Ожидается ссылка на ютуб контент</b>'

video_settings_message = (
    '<b>Настройки видео:</b>\n'
    '<blockquote>Музыка: <b>{music}</b>\n'
    'Громкость музыки: <b>{music_volume}</b>\n'
    'Заголовок видео: <b>{video_title}</b>\n'
    'Разрешение: <b>{resolution}</b></blockquote>\n'
    '<b>Субтитры:</b><b>{subtitles}</b>\n'
    '<blockquote>    Шрифт: <b>{font}</b>\n'
    '    Размер: <b>{size}</b>\n'
    '    Цвет: <b>{color}</b>\n'
    '    Максимум слов: <b>{max_words}</b>\n'
    '    Позиция: <b>{position}</b>\n'
    '    Обводка: <b>{outline}</b>\n'
    '    ---Размер: <b>{outline_size}</b>\n'
    '    ---Цвет: <b>{outline_color}</b>\n'
    '    Тень: <b>{shadow}</b>\n'
    '    ---Размер: <b>{shadow_size}</b>\n'
    '    ---Цвет: <b>{shadow_color}</b></blockquote>\n'
    '<b>Переводчик:</b> <b>{translator}</b>'
    '   <blockquote><b>{source_language}</b> --> <b>{translated_language}</b>\n'
    '    Скорость оригинала: <b>{original_speed}</b>\n'
    '    Скорость перевода: <b>{translation_speed}</b>\n'
    '<i> Умные субтитры:</i> <b>{smart_sub}</b></blockquote>\n'
    '<b> Нарезать видео:</b>'
    '   <b><pre>{timestamps}</pre></b>'
)

write_gpt_settings = """
<b>Введите настройки запроса</b>
"""

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
➖➖➖<b>OmniGpt</b>➖➖➖
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


settings_request = """
<b>Настройки запроса</b>:\n<pre><i>{0}</i></pre><i></i>\n\n<b>Температура ответа:</b>\n<blockquote><i>{1}</i></blockquote>
"""

water_mark_omnigpt = """
➖➖➖<b>OmniGpt</b>➖➖➖
<b>Время ответа:</b> <i>{0} сек</i> 
"""