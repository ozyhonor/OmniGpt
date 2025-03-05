import sqlite3

# Подключение к базе данных SQLite
conn = sqlite3.connect('db/users_.db')
cursor = conn.cursor()

# SQL-запрос для добавления новой колонки
cursor.execute("ALTER TABLE users ADD COLUMN similarity_threshold FLOAT CHECK (similarity_threshold >= 0 AND similarity_threshold <= 1) DEFAULT 0.5")
# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()
