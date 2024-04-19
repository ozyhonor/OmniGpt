import sqlite3


class DataBaseClass:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print(f"Успешное подключение к базе данных {self.db_name}")
        except sqlite3.Error as e:
            print(f"Ошибка при подключении к базе данных {self.db_name}: {e}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print(f"Отключение от базы данных {self.db_name}")

    def execute_query(self, query):
        try:
            if self.cursor:
                self.cursor.execute(query)
                self.connection.commit()
                print("Запрос выполнен успешно")
            else:
                print("Не удалось выполнить запрос. Нет активного курсора.")
        except sqlite3.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")

    def fetch_data(self, query):
        try:
            if self.cursor:
                self.cursor.execute(query)
                rows = self.cursor.fetchall()
                return rows
            else:
                print("Не удалось получить данные. Нет активного курсора.")
                return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных: {e}")
            return None

    def is_user_exist(self, user_id):
        self.cursor.execute('SELECT id FROM users WHERE id=?', (user_id,))
        return bool(self.cursor.fetchone())

    def add_user(self, user_id):
        self.cursor.execute('INSERT INTO users (id) VALUES (?)', (user_id,))
        self.connection.commit()

    def get_user_settings(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user_settings = self.cursor.fetchone()
        if user_settings is None:
            return {}
        return dict(zip([column[0] for column in self.cursor.description], user_settings))

    def add_settings(self, user_id, settings):
        self.cursor.execute('UPDATE users SET gpt = ? WHERE id = ?', (settings, user_id))
        self.connection.commit()

    def get_settings(self, user_id):
        self.cursor.execute('SELECT gpt FROM users WHERE id=?', (user_id,))
        return self.cursor.fetchone()[0]

    def add_degree(self, user_id, degree):
        self.cursor.execute('UPDATE users SET degree = ? WHERE id = ?', (degree, user_id))
        self.connection.commit()

    def get_degree(self, user_id):
        self.cursor.execute('SELECT degree FROM users WHERE id=?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_voice(self, user_id):
        self.cursor.execute('SELECT synthes_voice FROM users WHERE id=?', (user_id,))
        return self.cursor.fetchone()[0]

    def add_voice(self, user_id, synthes_voice):
        self.cursor.execute('UPDATE users SET synthes_voice = ? WHERE id = ?', (synthes_voice, user_id))
        self.connection.commit()

    def get_rate(self, user_id):
        self.cursor.execute('SELECT synthes_speed FROM users WHERE id=?', (user_id,))
        return self.cursor.fetchone()[0]

    def add_rate(self, user_id, synthes_speed):
        self.cursor.execute('UPDATE users SET synthes_speed = ? WHERE id = ?', (synthes_speed, user_id))
        self.connection.commit()

    def add_id_panel(self, user_id, id):
        self.cursor.execute('UPDATE users SET id_settings_panel = ? WHERE id = ?', (id, user_id))
        self.connection.commit()

    def get_id_panel(self, user_id):
        self.cursor.execute('SELECT id_settings_panel FROM users WHERE id=?', (user_id,))
        return self.cursor.fetchone()[0]

    def add_resolution(self, user_id, resolution):
        self.cursor.execute('UPDATE users SET resolution = ? WHERE id = ?', (resolution, user_id))
        self.connection.commit()

    def add_subtitles(self, user_id, subtitles):
        self.cursor.execute('UPDATE users SET subtitles = ? WHERE id = ?', (subtitles, user_id))
        self.connection.commit()

    def add_translator(self, user_id, translator):
        self.cursor.execute('UPDATE users SET translator = ? WHERE id = ?', (translator, user_id))
        self.connection.commit()

    def add_format(self, user_id, format):
        self.cursor.execute('UPDATE users SET format = ? WHERE id = ?', (format, user_id))
        self.connection.commit()

    def add_size(self, user_id, size):
        self.cursor.execute('UPDATE users SET size = ? WHERE id = ?', (size, user_id))
        self.connection.commit()

    def add_source_language(self, user_id, source_language):
        self.cursor.execute('UPDATE users SET source_language = ? WHERE id = ?', (source_language, user_id))
        self.connection.commit()

    def add_translated_language(self, user_id, translated_language):
        self.cursor.execute('UPDATE users SET translated_language = ? WHERE id = ?', (translated_language, user_id))
        self.connection.commit()

    def add_color(self, user_id, color):
        self.cursor.execute('UPDATE users SET color = ? WHERE id = ?', (color, user_id))
        self.connection.commit()

    def add_position(self, user_id, position):
        self.cursor.execute('UPDATE users SET position = ? WHERE id = ?', (position, user_id))
        self.connection.commit()

    def add_original_speed(self, user_id, original_speed):
        self.cursor.execute('UPDATE users SET original_speed = ? WHERE id = ?', (original_speed, user_id))
        self.connection.commit()

    def add_translation_speed(self, user_id, translation_speed):
        self.cursor.execute('UPDATE users SET translation_speed = ? WHERE id = ?', (translation_speed, user_id))
        self.connection.commit()

    def add_outline(self, user_id, outline):
        self.cursor.execute('UPDATE users SET outline = ? WHERE id = ?', (outline, user_id))
        self.connection.commit()

    def add_outline_size(self, user_id, outline_size):
        self.cursor.execute('UPDATE users SET outline_size = ? WHERE id = ?', (outline_size, user_id))
        self.connection.commit()

    def add_outline_color(self, user_id, outline_color):
        self.cursor.execute('UPDATE users SET outline_color = ? WHERE id = ?', (outline_color, user_id))
        self.connection.commit()

    def add_shadow(self, user_id, shadow):
        self.cursor.execute('UPDATE users SET shadow = ? WHERE id = ?', (shadow, user_id))
        self.connection.commit()

    def add_shadow_size(self, user_id, shadow_size):
        self.cursor.execute('UPDATE users SET shadow_size = ? WHERE id = ?', (shadow_size, user_id))
        self.connection.commit()

    def add_shadow_color(self, user_id, shadow_color):
        self.cursor.execute('UPDATE users SET shadow_color = ? WHERE id = ?', (shadow_color, user_id))
        self.connection.commit()

    def get_resolution(self, user_id):
        self.cursor.execute('SELECT resolution FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_subtitles(self, user_id):
        self.cursor.execute('SELECT subtitles FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_translator(self, user_id):
        self.cursor.execute('SELECT translator FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_timestamps(self, user_id):
        self.cursor.execute('SELECT timestamps FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_format(self, user_id):
        self.cursor.execute('SELECT format FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_size(self, user_id):
        self.cursor.execute('SELECT size FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_source_language(self, user_id):
        self.cursor.execute('SELECT source_language FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_translated_language(self, user_id):
        self.cursor.execute('SELECT translated_language FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_color(self, user_id):
        self.cursor.execute('SELECT color FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_position(self, user_id):
        self.cursor.execute('SELECT position FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_original_speed(self, user_id):
        self.cursor.execute('SELECT original_speed FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_translation_speed(self, user_id):
        self.cursor.execute('SELECT translation_speed FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_outline(self, user_id):
        self.cursor.execute('SELECT outline FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_outline_size(self, user_id):
        self.cursor.execute('SELECT outline_size FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_outline_color(self, user_id):
        self.cursor.execute('SELECT outline_color FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_shadow(self, user_id):
        self.cursor.execute('SELECT shadow FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_shadow_size(self, user_id):
        self.cursor.execute('SELECT shadow_size FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_shadow_color(self, user_id):
        self.cursor.execute('SELECT shadow_color FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_quality(self, user_id):
        self.cursor.execute('SELECT quality FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def add_timestamps(self, user_id, timestamps):
        self.cursor.execute('UPDATE users SET timestamps = ? WHERE id = ?', (timestamps, user_id))
        self.connection.commit()

    def add_font(self, user_id, font):
        self.cursor.execute('UPDATE users SET font = ? WHERE id = ?', (font, user_id))
        self.connection.commit()

    def get_font(self, user_id):
        self.cursor.execute('SELECT font FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def get_max_words(self, user_id):
        self.cursor.execute('SELECT max_words FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def add_max_words(self, user_id, max_words):
        self.cursor.execute('UPDATE users SET max_words = ? WHERE id = ?', (max_words, user_id))
        self.connection.commit()

    def get_smart_sub(self, user_id):
        self.cursor.execute('SELECT smart_sub FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def add_smart_sub(self, user_id, smart_sub):
        self.cursor.execute('UPDATE users SET smart_sub = ? WHERE id = ?', (smart_sub, user_id))
        self.connection.commit()


    def close(self):
        self.disconnect()

db = DataBaseClass('./db/users_.db')


