import sqlite3

# Подключение к базе данных SQLite
conn = sqlite3.connect('db/users_.db')
cursor = conn.cursor()

#'🚀 Креативность', '🧠 Логика', '🦄 Уникальность'

cursor.execute("ALTER TABLE users ADD COLUMN frequency_penalty_gpt FLOAT CHECK (frequency_penalty_gpt >= -2 AND frequency_penalty_gpt <= 2) DEFAULT 0 ")
cursor.execute("ALTER TABLE users ADD COLUMN presence_penalty_gpt  FLOAT CHECK (presence_penalty_gpt >= -2 AND presence_penalty_gpt <= 2) DEFAULT 0 ")
cursor.execute("ALTER TABLE users ADD COLUMN reasoning_effort_gpt TEXT DEFAULT 'medium'")

conn.commit()
conn.close()
