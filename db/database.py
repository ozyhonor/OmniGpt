import sqlite3
import aiosqlite
import asyncio


class DataBaseClass:
    def __init__(self, db_name):
        self.db_name = db_name

    async def is_user_exist(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT id FROM users WHERE id = ?', (user_id,)) as cursor:
                setting = await cursor.fetchone()
                if setting is None:
                    return False
                return bool(setting[0])

    async def add_new_user(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('INSERT INTO users (id) VALUES (?)', (user_id,)) as cursor:
                await db.commit()

    async def get_all_user_settings(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM users WHERE id=?', (user_id,)) as cursor:
                settings = await cursor.fetchone()
                return dict(zip([column[0] for column in cursor.description], settings)) if settings else {}

    async def update_user_setting(self, key, value, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(f'UPDATE users SET {key} = ? WHERE id = ?', (value, user_id)) as cursor:
                await db.commit()

    async def get_user_setting(self, key, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(f'SELECT {key} FROM users WHERE id=?', (user_id,)) as cursor:
                setting = await cursor.fetchone()
                return setting[0] if setting else None


db = DataBaseClass('db/users_.db')




