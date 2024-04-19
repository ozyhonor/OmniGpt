from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_reader import telegram_token
from aiogram.enums import ParseMode


storage = MemoryStorage()
bot = Bot(token=telegram_token, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=storage)

