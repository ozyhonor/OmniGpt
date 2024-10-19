import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('db/users_.db')
cursor = conn.cursor()


# Добавление новых столбцов в таблицу users
def add_columns():
    cursor.execute("""
        ALTER TABLE users ADD COLUMN vision_id_panel INTEGER DEFAULT 0
    """)

    # Сохранить изменения
    conn.commit()


# Добавление новых столбцов
add_columns()

# Закрытие соединения
conn.close()