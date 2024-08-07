from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import os




class CustomKeyboard:
    def __init__(self):
        self.reply_markup = None


    @staticmethod
    def create_inline_kb_gpt_settings():
        names_settings_gpt = ['⚙️ Настройки', '🌡 Градус']
        builder = InlineKeyboardBuilder()
        for name in names_settings_gpt:
            builder.button(text=f"{name}", callback_data=f"{name}")

        return builder

    @staticmethod
    def create_inline_kb_default_settings():

        builder = InlineKeyboardBuilder()
        builder.button(text=f"Оставить текущие настройки.", callback_data="video_cancel")

        return builder.as_markup()

    @staticmethod
    def inline_translated_languages_for_translator():
        builder = InlineKeyboardBuilder()
        languages = [
            {'code': 'en', 'flag': '🇬🇧', 'name': 'English'},
            {'code': 'es', 'flag': '🇪🇸', 'name': 'Spanish'},
            {'code': 'fr', 'flag': '🇫🇷', 'name': 'French'},
            {'code': 'ru', 'flag': '🇷🇺', 'name': 'Russian'},
            {'code': 'zh-cn', 'flag': '🇨🇳', 'name': 'Chinese (Simplified)'},
            {'code': 'ar', 'flag': '🇸🇦', 'name': 'Arabic'},
            {'code': 'pt', 'flag': '🇵🇹', 'name': 'Portuguese'},
            {'code': 'de', 'flag': '🇩🇪', 'name': 'German'},
            {'code': 'ja', 'flag': '🇯🇵', 'name': 'Japanese'},
            {'code': 'hi', 'flag': '🇮🇳', 'name': 'Hindi'},
            {'code': 'it', 'flag': '🇮🇹', 'name': 'Italian'},
            {'code': 'ko', 'flag': '🇰🇷', 'name': 'Korean'},
        ]
        for i in range(0, len(languages), 6):
            row = languages[i:i + 6]
            buttons_row = [
                InlineKeyboardButton(text=language['flag'] + ' ' + language['name'],
                                     callback_data=f'translator_dest_lang:{language["code"]}') for
                language in row
            ]
            builder.row(*buttons_row)
        return builder.as_markup()
    @staticmethod
    def create_queue_button():
        names_gender = ['✅ Выполнить', '🎛 Настройка']
        builder = InlineKeyboardBuilder()
        for name in names_gender:
            builder.button(text=f"{name}", callback_data=f"{name}")
        return builder

    @staticmethod
    def create_stop_button():

        builder = InlineKeyboardBuilder()
        builder.button(text=f"Остановить", callback_data="stop_gpt")

        return builder

    @staticmethod
    def create_translator_buttons():

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='◀️ Назад'),
                    KeyboardButton(text='📧Текст'),
                    KeyboardButton(text='🗃 Файл')
                ]
                ],  resize_keyboard=True)

        return keyboard

    @staticmethod
    def create_stop_eden_button():

        builder = InlineKeyboardBuilder()
        builder.button(text=f"Остановить", callback_data="stop_eden")

        return builder
    @staticmethod
    def create_youtube_buttons():

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='◀️ Назад'),
                    KeyboardButton(text='📥 Скачать')
                    #KeyboardButton(text='💽 Плейлист')
                ]
                ],  resize_keyboard=True)

        return keyboard

    @staticmethod
    def create_format_buttons():

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='◀️ Назад'),
                    KeyboardButton(text='📥 Скачать')
                    #KeyboardButton(text='💽 Плейлист')
                ]
                ],  resize_keyboard=True)

        return keyboard

    @staticmethod
    def create_gpt_buttons():

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='◀️ Назад'),
                    KeyboardButton(text='🗒 Текст'),
                    KeyboardButton(text='🗂 Файл'),
                    KeyboardButton(text='🗄 Очередь')
                ]
                ],  resize_keyboard=True)

        return keyboard


    @staticmethod
    def create_inline_speech_settings():

        names_settings_speech = ['🔊 Скорость', '🗣 Голос']
        builder = InlineKeyboardBuilder()
        for name in names_settings_speech:
            builder.button(text=f"{name}", callback_data=f"{name}")
        return builder

    @staticmethod
    def create_speech_main():

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='◀️ Назад'),
                    KeyboardButton(text='✉️ Сообщение'),
                    KeyboardButton(text='📁 Файл')
                ]
                ],  resize_keyboard=True)

        return keyboard



    @staticmethod
    def create_acsess():
        names_gender = ['✅ ᚢᚹᛋᚺᚱᛠⰓ', '❌ ᛜᛠᛕᚳᛜᚺᛋᛠⰓ']
        builder = InlineKeyboardBuilder()
        for name in names_gender:
            builder.button(text=f"{name}", callback_data=f"{name}")
        return builder


    @staticmethod
    def create_reply_main_menu():

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='🤖 ChatGpt'),
                    KeyboardButton(text='🎧 Озвучка'),
                    KeyboardButton(text='🚩 Ютуб'),
                    KeyboardButton(text='🔄 Перевод'),
                    KeyboardButton(text='🎥 Видео')
                ]
                ],  resize_keyboard=True)

        return keyboard

    @staticmethod
    def inline_timestamps_settings():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='🔹Кроп', callback_data='timestamps')
        )
        return builder.as_markup()


    @staticmethod
    def inline_crop_menu(timestamps):
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='🔹Кроп', callback_data='timestamps')
        )
        if timestamps != ['0']:
            for i in timestamps:
                builder.row(InlineKeyboardButton(text='❌', callback_data=f'cancel_stamp;{i}'),
                            InlineKeyboardButton(text=f'{i}', callback_data=f'timestamps;{i}'))

        builder.row(
            InlineKeyboardButton(text='➕ Добавить', callback_data='add_new_stamp')
        )
        builder.row(
            InlineKeyboardButton(text='Интересные моменты', callback_data='interesting_moment')
        )
        builder.row(
            InlineKeyboardButton(text='❌ Очистить все', callback_data='clear_all_stamp')
        )
        return builder.as_markup()


    @staticmethod
    def inline_translator_settings():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='🔹Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(InlineKeyboardButton(text='Язык оригинала', callback_data='source_language'),
                    InlineKeyboardButton(text='Язык перевода', callback_data='translated_language'))
        builder.row(
            InlineKeyboardButton(text='Скорость оригинала', callback_data='original_speed'),
            InlineKeyboardButton(text='Скорость перевода', callback_data='translated_speed'),
        )
        builder.row(InlineKeyboardButton(text='Нахлест', callback_data='overlap'))
        return builder.as_markup()


    @staticmethod
    def inline_overlap_change():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='🔹Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='100', callback_data='overlap:100'),
            InlineKeyboardButton(text='200', callback_data='overlap:200'),
            InlineKeyboardButton(text='300', callback_data='overlap:300'),
            InlineKeyboardButton(text='400', callback_data='overlap:400'),
            InlineKeyboardButton(text='500', callback_data='overlap:500'),
        )
        builder.row(
            InlineKeyboardButton(text='600', callback_data='overlap:600'),
            InlineKeyboardButton(text='700', callback_data='overlap:700'),
            InlineKeyboardButton(text='800', callback_data='overlap:800'),
            InlineKeyboardButton(text='900', callback_data='overlap:900'),
            InlineKeyboardButton(text='1000', callback_data='overlap:1000'),
        )
        builder.row(
            InlineKeyboardButton(text='0', callback_data='overlap:0'))

        return builder.as_markup()


    @staticmethod
    def inline_translated_languages():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='🔹Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        languages = [
            {'code': 'en', 'flag': '🇬🇧', 'name': 'English'},
            {'code': 'es', 'flag': '🇪🇸', 'name': 'Spanish'},
            {'code': 'fr', 'flag': '🇫🇷', 'name': 'French'},
            {'code': 'ru', 'flag': '🇷🇺', 'name': 'Russian'},
            {'code': 'zh-cn', 'flag': '🇨🇳', 'name': 'Chinese (Simplified)'},
            {'code': 'ar', 'flag': '🇸🇦', 'name': 'Arabic'},
            {'code': 'pt', 'flag': '🇵🇹', 'name': 'Portuguese'},
            {'code': 'de', 'flag': '🇩🇪', 'name': 'German'},
            {'code': 'ja', 'flag': '🇯🇵', 'name': 'Japanese'},
            {'code': 'hi', 'flag': '🇮🇳', 'name': 'Hindi'},
            {'code': 'it', 'flag': '🇮🇹', 'name': 'Italian'},
            {'code': 'ko', 'flag': '🇰🇷', 'name': 'Korean'},
        ]
        for i in range(0, len(languages), 6):
            row = languages[i:i + 6]
            buttons_row = [
                InlineKeyboardButton(text=language['flag'] + ' ' + language['name'],
                                     callback_data=f'translated_language:{language["code"]}') for
                language in row
            ]
            builder.row(*buttons_row)
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_language_translated')
        )
        return builder.as_markup()


    @staticmethod
    def inline_resolution():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='🔹Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(InlineKeyboardButton(text='720x1280', callback_data='resolution:720x1280'),
                    InlineKeyboardButton(text='Original', callback_data='resolution:original'))
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_resolution')
        )
        return builder.as_markup()

    @staticmethod
    def inline_size():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='🔹Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='28', callback_data='size:28'),
            InlineKeyboardButton(text='30', callback_data='size:30'),
            InlineKeyboardButton(text='32', callback_data='size:32'),
            InlineKeyboardButton(text='34', callback_data='size:34'),
            InlineKeyboardButton(text='36', callback_data='size:36'),
            InlineKeyboardButton(text='38', callback_data='size:38'),
        ),
        builder.row(
            InlineKeyboardButton(text='40', callback_data='size:40'),
            InlineKeyboardButton(text='42', callback_data='size:42'),
            InlineKeyboardButton(text='44', callback_data='size:44'),
            InlineKeyboardButton(text='46', callback_data='size:46'),
            InlineKeyboardButton(text='48', callback_data='size:48'),
            InlineKeyboardButton(text='50', callback_data='size:50'),
        ),
        builder.row(
            InlineKeyboardButton(text='52', callback_data='size:52'),
            InlineKeyboardButton(text='54', callback_data='size:54'),
            InlineKeyboardButton(text='56', callback_data='size:56'),
            InlineKeyboardButton(text='58', callback_data='size:58'),
            InlineKeyboardButton(text='60', callback_data='size:60'),
            InlineKeyboardButton(text='62', callback_data='size:62'),
        )
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_size')
        )
        return builder.as_markup()

#🔴🟠🟡🟢🔵🟣⚫️⚪️🟤
    @staticmethod
    def inline_color():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='🔹Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='🔴', callback_data='color:firebrick'),
            InlineKeyboardButton(text='🟠', callback_data='color:coral'),
            InlineKeyboardButton(text='🟡', callback_data='color:Gold'),
            InlineKeyboardButton(text='🟢', callback_data='color:green'),
            InlineKeyboardButton(text='🔵', callback_data='color:blue'),
            InlineKeyboardButton(text='🟣', callback_data='color:purple'),
            InlineKeyboardButton(text='⚫️', callback_data='color:black'),
            InlineKeyboardButton(text='⚪️', callback_data='color:ivory')
        )
        builder.row(
            InlineKeyboardButton(text='Отправьте Hex код цвета', callback_data='hex_code')
        )
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_color')
        )
        return builder.as_markup()

    @staticmethod
    def create_voice_menu():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='alloy', callback_data='change_voice:alloy'),
            InlineKeyboardButton(text='echo', callback_data='change_voice:echo'),
            InlineKeyboardButton(text='fable', callback_data='change_voice:fable'),
            InlineKeyboardButton(text='onyx', callback_data='change_voice:onyx'),
            InlineKeyboardButton(text='nova', callback_data='change_voice:nova'),
            InlineKeyboardButton(text='shimmer', callback_data='change_voice:shimmer'),
        )
        builder.row(InlineKeyboardButton(text='Отмена', callback_data='video_cancel'))
        return builder.as_markup()

    @staticmethod
    def inline_youtube_settings():
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Субтитры', callback_data='download_from_yt:subtitles'),
                    InlineKeyboardButton(text='Видео', callback_data='download_from_yt:video'),
                    InlineKeyboardButton(text='Аудио', callback_data='download_from_yt:audio'))
        return builder.as_markup()


    @staticmethod
    def inline_cancel():
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Отмена', callback_data='video_cancel'))
        return builder.as_markup()

    @staticmethod
    def inline_subtitles_settings():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='🔹Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='Размер', callback_data='size'),
            InlineKeyboardButton(text='Цвет', callback_data='color'),
            InlineKeyboardButton(text='Позиция', callback_data='position'),
            InlineKeyboardButton(text='Шрифт', callback_data='font')
        )
        builder.row(
            InlineKeyboardButton(text='Обводка', callback_data='outline'),
            InlineKeyboardButton(text='Цвет', callback_data='color_outline'),
            InlineKeyboardButton(text='Размер', callback_data='size_outline'),
        )
        builder.row(
            InlineKeyboardButton(text='Тень', callback_data='shadow'),
            InlineKeyboardButton(text='Цвет', callback_data='color_shadow'),
            InlineKeyboardButton(text='Размер', callback_data='size_shadow'),
        )
        builder.row(InlineKeyboardButton(text='Максимум слов', callback_data='max_words'))
        return builder.as_markup()

    @staticmethod
    def inline_font():
        builder = InlineKeyboardBuilder()
        fonts = os.listdir('fonts')
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='🔹Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )

        for x,font in enumerate(fonts):
            builder.row(InlineKeyboardButton(text=f'{font}', callback_data=f'font:{font}'))

        builder.row(
            InlineKeyboardButton(text='▪️Загрузить шрифт▪️', callback_data='upload_font')
        )
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_color')
        )
        return builder.as_markup()


    @staticmethod
    def inline_position():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='🔹Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )

        builder.row(InlineKeyboardButton(text='Верх', callback_data='position:Верх'))
        builder.row(InlineKeyboardButton(text='Середина', callback_data='position:Середина'))
        builder.row(InlineKeyboardButton(text='Низ', callback_data='position:Низ'))
        builder.row(InlineKeyboardButton(text='Координаты', callback_data='x_y_subtitles'))
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_color')
        )
        return builder.as_markup()

    @staticmethod
    def inline_shadow_color():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='🔹Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='🔴', callback_data='shadow_color:firebrick'),
            InlineKeyboardButton(text='🟠', callback_data='shadow_color:coral'),
            InlineKeyboardButton(text='🟡', callback_data='shadow_color:Gold'),
            InlineKeyboardButton(text='🟢', callback_data='shadow_color:green'),
            InlineKeyboardButton(text='🔵', callback_data='shadow_color:blue'),
            InlineKeyboardButton(text='🟣', callback_data='shadow_color:purple'),
            InlineKeyboardButton(text='⚫️', callback_data='shadow_color:black'),
            InlineKeyboardButton(text='⚪️', callback_data='shadow_color:ivory')
        )
        builder.row(
            InlineKeyboardButton(text='Отправьте Hex код цвета', callback_data='hex_code_shadow')
        )
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_color')
        )
        return builder.as_markup()

    @staticmethod
    def inline_outline_color():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='🔹Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='🔴', callback_data='outline_color:firebrick'),
            InlineKeyboardButton(text='🟠', callback_data='outline_color:coral'),
            InlineKeyboardButton(text='🟡', callback_data='outline_color:Gold'),
            InlineKeyboardButton(text='🟢', callback_data='outline_color:green'),
            InlineKeyboardButton(text='🔵', callback_data='outline_color:blue'),
            InlineKeyboardButton(text='🟣', callback_data='outline_color:purple'),
            InlineKeyboardButton(text='⚫️', callback_data='outline_color:black'),
            InlineKeyboardButton(text='⚪️', callback_data='outline_color:ivory')
        )
        builder.row(
            InlineKeyboardButton(text='Отправьте Hex код цвета', callback_data='hex_code_outline')
        )
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_color')
        )
        return builder.as_markup()


    @staticmethod
    def inline_original_speed():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='🔹Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='0.5', callback_data='original_speed:0.5'),
            InlineKeyboardButton(text='0.6', callback_data='original_speed:0.625'),
            InlineKeyboardButton(text='0.8', callback_data='original_speed:0.8'),
        )
        builder.row(InlineKeyboardButton(text='1', callback_data='original_speed:1'))
        builder.row(
            InlineKeyboardButton(text='1.2', callback_data='original_speed:1.2'),
            InlineKeyboardButton(text='1.4', callback_data='original_speed:1.4'),
            InlineKeyboardButton(text='1.6', callback_data='original_speed:1.6'),
            InlineKeyboardButton(text='1.8', callback_data='original_speed:1.8'),
            InlineKeyboardButton(text='1.9', callback_data='original_speed:1.9')

        )
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_original_lang')
        )
        return builder.as_markup()




    @staticmethod
    def inline_translated_speed():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='🔹Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='0.2', callback_data='translated_speed:0.2'),
            InlineKeyboardButton(text='0.4', callback_data='translated_speed:0.4'),
            InlineKeyboardButton(text='0.6', callback_data='translated_speed:0.6'),
            InlineKeyboardButton(text='0.8', callback_data='translated_speed:0.8'),
            InlineKeyboardButton(text='0.9', callback_data='translated_speed:0.9'),
        )
        builder.row(InlineKeyboardButton(text='1', callback_data='translated_speed:1'))
        builder.row(
            InlineKeyboardButton(text='1.2', callback_data='translated_speed:1.2'),
            InlineKeyboardButton(text='1.4', callback_data='translated_speed:1.4'),
            InlineKeyboardButton(text='1.6', callback_data='translated_speed:1.6'),
            InlineKeyboardButton(text='1.8', callback_data='translated_speed:1.8'),
            InlineKeyboardButton(text='1.9', callback_data='translated_speed:1.9')

        )
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_original_lang')
        )
        return builder.as_markup()







    @staticmethod
    def inline_max_words():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='🔹Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='Умные субтитры', callback_data='smart_subtitles'))
        builder.row(
            InlineKeyboardButton(text='1', callback_data='max_words:1'),
            InlineKeyboardButton(text='2', callback_data='max_words:2'),
            InlineKeyboardButton(text='3', callback_data='max_words:3'),
            InlineKeyboardButton(text='4', callback_data='max_words:4'),
            InlineKeyboardButton(text='5', callback_data='max_words:5'),
            InlineKeyboardButton(text='6', callback_data='max_words:6')
        )
        builder.row(
            InlineKeyboardButton(text='7', callback_data='max_words:7'),
            InlineKeyboardButton(text='8', callback_data='max_words:8'),
            InlineKeyboardButton(text='9', callback_data='max_words:9'),
            InlineKeyboardButton(text='10', callback_data='max_words:10'),
            InlineKeyboardButton(text='11', callback_data='max_words:11'),
            InlineKeyboardButton(text='12', callback_data='max_words:12')
        )
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_color')
        )
        return builder.as_markup()


    @staticmethod
    def inline_size_shadow():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='🔹Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='1', callback_data='shadow_size:1'),
            InlineKeyboardButton(text='2', callback_data='shadow_size:2'),
            InlineKeyboardButton(text='3', callback_data='shadow_size:3'),
            InlineKeyboardButton(text='4', callback_data='shadow_size:4'),
            InlineKeyboardButton(text='5', callback_data='shadow_size:5'),
            InlineKeyboardButton(text='6', callback_data='shadow_size:6')
        )
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_color')
        )
        return builder.as_markup()

    @staticmethod
    def create_music_frame():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='🔹Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        music = os.listdir('music')
        for x,music in enumerate(music):
            builder.row(InlineKeyboardButton(text=f'{music}', callback_data=f'music:{music}'))

        builder.row(
            InlineKeyboardButton(text='▪️Загрузить музыку▪️', callback_data='upload_music')
        )
        builder.row(
            InlineKeyboardButton(text='🔊 Громкость', callback_data='volume_music')
        )
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_resolution')
        )
        return builder.as_markup()

    @staticmethod
    def inline_outline_size():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='🔹Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='1', callback_data='outline_size:1'),
            InlineKeyboardButton(text='2', callback_data='outline_size:2'),
            InlineKeyboardButton(text='3', callback_data='outline_size:3'),
            InlineKeyboardButton(text='4', callback_data='outline_size:4'),
            InlineKeyboardButton(text='5', callback_data='outline_size:5'),
            InlineKeyboardButton(text='6', callback_data='outline_size:6')
        )
        builder.row(
            InlineKeyboardButton(text='🔙 Назад', callback_data='back_color')
        )
        return builder.as_markup()

    @staticmethod
    def inline_video_settings():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='🔹Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Перевод', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.row(
            InlineKeyboardButton(text='Формат', callback_data='format'),
            InlineKeyboardButton(text='Музыка', callback_data='music'),
            InlineKeyboardButton(text='Разрешение', callback_data='resolution')
        )
        builder.adjust(4)
        return builder.as_markup()

    @staticmethod
    def create_inline_video_settings_buttons():
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Видео', callback_data='video_settings'),
            InlineKeyboardButton(text='Субтитры', callback_data='subtitles'),
            InlineKeyboardButton(text='Переводчик', callback_data='translator'),
            InlineKeyboardButton(text='Кроп', callback_data='timestamps')
        )
        builder.adjust(4)

        return builder.as_markup()


    @staticmethod
    def create_video_main():

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='◀️ Назад'),
                    KeyboardButton(text='🛠️ Создать видео')
                ]
                ],  resize_keyboard=True)

        return keyboard

    @staticmethod
    def create_pls_accept():

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='🙏 Доступ')
                ]
                ],  resize_keyboard=True)

        return keyboard




