import sqlite3

# Подключение к базе данных SQLite
conn = sqlite3.connect('db/users_.db')
cursor = conn.cursor()

# Выполнение команды для добавления нового столбца
try:
    cursor.execute("ALTER TABLE users ADD COLUMN download_language_subtitles TEXT DEFAULT 'ru';")
    conn.commit()
    print("Поле download_language_subtitles успешно добавлено.")
except sqlite3.OperationalError as e:
    print(f"Ошибка: {e}")
finally:
    # Закрытие соединения
    conn.close()
