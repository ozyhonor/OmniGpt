from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from db.database import db
from menu.keyboards import CustomKeyboard
from aiogram.types import InputTextMessageContent, InlineQueryResultArticle
from states.states import WaitingYoutube
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list, as_marked_section, as_key_value, HashTag, Bold
from aiogram.types.text_quote import TextQuote
from aiogram.methods.get_custom_emoji_stickers import GetCustomEmojiStickers
start_router = Router()
from spawnbot import bot
from aiogram.types.sticker import Sticker
from typing import List
@start_router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    print(message.from_user.id)
    markup = CustomKeyboard.create_reply_main_menu()
    markup_accept = CustomKeyboard.create_pls_accept()
    user_id = message.from_user.id
    db.connect()
    if not db.is_user_exist(user_id):
        await message.answer(f"Привет, <b>{message.from_user.full_name}</b> !, получите доступ", reply_markup=markup_accept)
    else:
        await message.answer(f"Привет, <b>{message.from_user.full_name}!</b>", reply_markup=markup)
    db.disconnect()


@start_router.message(Command("go"))
async def command_start_handler(message: Message) -> None:
    print(message.from_user.id)
    emoji_id = '5447644880824181073'
    await bot.send_message(message.chat.id, '<tg-emoji emoji-id="5447410659077661506">🌐</tg-emoji>', parse_mode='html')
    db.connect()

    text = '''
<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<u>underline</u>, <ins>underline</ins>
<s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
<span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
<b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=123456789">inline mention of a user</a>
<tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
<pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
<blockquote>Block quotation started\nBlock quotation continued\nThe last line of the block quotation</blockquote>'''
    await message.answer(text=text)

    db.disconnect()