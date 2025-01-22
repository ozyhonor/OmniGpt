from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_reader import telegram_token


storage = MemoryStorage()
bot = Bot(token=telegram_token, parse_mode='HTML')
dp = Dispatcher(storage=storage)

