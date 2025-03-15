import sqlite3

# Подключение к базе данных SQLite
conn = sqlite3.connect('db/users_.db')
cursor = conn.cursor()

#
# SQL-запрос для добавления новой колонки
cursor.execute("ALTER TABLE users ADD COLUMN synthesis_language TEXT DEFAULT 'ru'")
cursor.execute("ALTER TABLE users ADD COLUMN synthesis_response_format TEXT DEFAULT 'text'")
cursor.execute("ALTER TABLE users ADD COLUMN id_synthesis_panel INTEGER DEFAULT 0")

conn.commit()
conn.close()
