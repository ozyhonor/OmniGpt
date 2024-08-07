import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('db/users_.db')
cursor = conn.cursor()

# Добавление новых полей
cursor.execute("ALTER TABLE users ADD COLUMN dest_lang TEXT DEFAULT 'en'")
cursor.execute("ALTER TABLE users ADD COLUMN translator_id_panel INTEGER DEFAULT 0")

# Сохранение изменений
conn.commit()
