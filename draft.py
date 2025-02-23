import sqlite3

# Подключение к базе данных SQLite
conn = sqlite3.connect('db/users_.db')
cursor = conn.cursor()

# SQL-запрос для добавления новой колонки
cursor.execute("UPDATE users SET split_play_list = '#*#*#' WHERE id = 1863201456")

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()
