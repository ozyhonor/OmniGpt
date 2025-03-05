import sqlite3

# Подключение к базе данных SQLite
conn = sqlite3.connect('db/users_.db')
cursor = conn.cursor()

# SQL-запрос для добавления новой колонки
cursor.execute("ALTER TABLE users ADD COLUMN picture_model TEXT DEFAULT 'dall-e-2'")
cursor.execute("ALTER TABLE users ADD COLUMN picture_prompt TEXT DEFAULT 'Нарисуй картину маслом.'")
cursor.execute("ALTER TABLE users ADD COLUMN picture_size TEXT DEFAULT '1024x1024'")
cursor.execute("ALTER TABLE users ADD COLUMN picture_count INTEGER CHECK (picture_count >= 1 AND synthes_speed <= 10) DEFAULT 1")
cursor.execute("ALTER TABLE users ADD COLUMN id_picture_panel INTEGER DEFAULT 0")
cursor.execute("ALTER TABLE users ADD COLUMN similarity_threshold FLOAT CHECK (similarity_threshold >= 0 AND similarity_threshold <= 1) DEFAULT 0.5")
# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()
