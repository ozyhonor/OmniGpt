import sqlite3

conn = sqlite3.connect('users_.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    gpt TEXT DEFAULT 'You have to compress texts to 100-150 characters revealing the main essence. Always give answers in Russian. No need to write what you did, just give me a compressed text in response.',
    degree FLOAT CHECK (degree >= 0 AND degree <= 1) DEFAULT 0,
    synthes_voice TEXT CHECK (synthes_voice IN ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer')) DEFAULT 'nova',
    synthes_speed FLOAT CHECK (synthes_speed >= 0.25 AND synthes_speed <= 4.0) DEFAULT 1,
    access BOOLEAN DEFAULT 0,
    resolution TEXT DEFAULT 'original',
    subtitles BOOLEAN DEFAULT 0,
    translator BOOLEAN DEFAULT 0,
    timestamps TEXT DEFAULT '0',
    format TEXT DEFAULT 'MP4',
    size INTEGER DEFAULT 16,
    source_language TEXT DEFAULT 'AI',
    translated_language DEFAULT 'ru',
    color TEXT DEFAULT 'White',
    position TEXT DEFAULT 'center',
    original_speed FLOAT DEFAULT 1,
    translation_speed FLOAT DEFAULT 1,
    outline BOOLEAN DEFAULT 0,
    outline_size INTEGER DEFAULT 0,
    outline_color TEXT DEFAULT 'Black',
    shadow BOOLEAN DEFAULT 0,
    shadow_size INTEGER DEFAULT 0,
    shadow_color TEXT DEFAULT 'Yellow',
    font TEXT DEFAULT 'GeorgiaPro-SemiBold',
    quality TEXT DEFAULT 'original',
    max_words INTEGER DEFAULT 1,
    smart_sub BOOLEAN DEFAULT 0,
    resolution TEXT DEFAULT 'Original',
    id_settings_panel INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()
