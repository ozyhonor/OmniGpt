import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('users_.db')
cursor = conn.cursor()

# Создание таблицы пользователей
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    -- Глобальные переменные (для Telegram-бота)
    id INTEGER PRIMARY KEY,
    id_picture_panel INTEGER DEFAULT 0,
    id_settings_panel INTEGER DEFAULT 0,
    id_gpt_panel INTEGER DEFAULT 0,
    id_speech_panel INTEGER DEFAULT 0,
    id_youtube_panel INTEGER DEFAULT 0,
    id_vision_panel INTEGER DEFAULT 0,
    translator_id_panel INTEGER DEFAULT 0,

    -- Настройки для генирации изображения
    picture_model TEXT DEFAULT 'dall-e-2',
    picture_prompt TEXT DEFAULT 'Нарисуй картину маслом.',
    picture_size TEXT DEFAULT '1024x1024',
    picture_count INTEGER CHECK (picture_count >= 1 AND synthes_speed <= 10) DEFAULT 1,

    -- Настройки для GPT-чата
    gpt TEXT DEFAULT 'You have to compress texts to 100-150 characters revealing the main essence. Always give answers in Russian. No need to write what you did, just give me a compressed text in response.',
    gpt_model TEXT DEFAULT 'gpt-3.5-turbo',
    gpt_tokens TEXT CHECK (
        (gpt_tokens GLOB '[0-9]*' AND CAST(gpt_tokens AS INTEGER) BETWEEN 100 AND 128000) 
        OR (LENGTH(gpt_tokens) <= 11)
    ) DEFAULT '4096',
    degree FLOAT CHECK (degree >= 0 AND degree <= 1) DEFAULT 0,
    postprocess_bool BOOLEAN DEFAULT 0,

    -- Настройки для озвучки
    synthes_voice TEXT CHECK (synthes_voice IN ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer')) DEFAULT 'nova',
    synthes_speed FLOAT CHECK (synthes_speed >= 0.25 AND synthes_speed <= 4.0) DEFAULT 1,

    -- Настройки для переводчика
    translated_language TEXT DEFAULT 'ru',
    

    -- Настройки для скачивания из YouTube
    download_subtitles BOOLEAN DEFAULT 0,
    download_video BOOLEAN DEFAULT 0,
    download_audio BOOLEAN DEFAULT 0,
    download_language_subtitles TEXT DEFAULT 'ru',
    split_play_list TEXT DEFAULT '#*#*#',
    

    -- Настройки для обработки видео
    resolution TEXT DEFAULT 'original',
    format TEXT DEFAULT 'MP4',
    quality TEXT DEFAULT 'original',
    translator BOOLEAN DEFAULT 0,
    intrested_moment ,
    -- Нарезать видео
    interesting_moment BOOLEAN DEFAULT 0,
    timestamps TEXT DEFAULT '0',
    
    -- Общие настройки видео
    video_title TEXT DEFAULT '',
    overlap INTEGER DEFAULT 0,
    
    -- Настройки для видео переводчика
    original_speed FLOAT DEFAULT 1,
    translation_speed FLOAT DEFAULT 1,
    
    -- Подгруппа "Субтитры"
    subtitles BOOLEAN DEFAULT 0,
    font_size INTEGER DEFAULT 16,
    font TEXT DEFAULT 'GeorgiaPro-SemiBold',
    position TEXT DEFAULT 'center',
    dest_lang TEXT DEFAULT 'en',
    source_language TEXT DEFAULT 'AI',
    primary_color TEXT DEFAULT '255,255,255,0',
    translated_color TEXT DEFAULT '255,255,255,0',
    second_color TEXT DEFAULT '255,255,255,0',
    outline BOOLEAN DEFAULT 0,
    outline_size INTEGER DEFAULT 0,
    outline_color TEXT DEFAULT '0,0,0,0',
    smart_sub BOOLEAN DEFAULT 0,
    background BOOLEAN DEFAULT 0,
    background_color TEXT DEFAULT '0,0,0,0',
    max_words INTEGER DEFAULT 1,
    shadow BOOLEAN DEFAULT 0,
    shadow_color TEXT DEFAULT '255,255,255,0',

    -- Подгруппа "Музыка"
    music TEXT DEFAULT 'None',
    volume_music INTEGER CHECK (volume_music >= 1 AND volume_music <= 100) DEFAULT 20,

    -- Постпроцессинг (GPT и Vision)
    vision_prompt TEXT DEFAULT '-',
    vision_model TEXT DEFAULT 'gpt-4o'
)
""")

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()
