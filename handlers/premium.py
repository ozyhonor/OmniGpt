from spawnbot import bot
from config_reader import admins_ids
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
import string
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingPremium
from menu.keyboards import CustomKeyboard
from aiogram.types import Message, CallbackQuery
import asyncio
from utils.gpt_requests import chunks_request, solo_request

premium_router = Router()

def compare_texts(text1, text2):
    # Разбиваем текст на слова
    words1 = text1.split()
    words2 = text2.split()
    def clean_word(word):
        return word.translate(str.maketrans('', '', string.punctuation)).lower()

    # Проверяем, что каждое слово из первого текста содержится в соответствующем слове второго
    for i, (w1, w2) in enumerate(zip(words1, words2)):
        if clean_word(w1) not in clean_word(w2):
            return False, f"Несовпадение на слове {i + 1}: '{w1}' не содержится в '{w2}'"

    # Проверяем, совпадает ли количество слов
    if len(words1) != len(words2):
        return False, "Количество слов не совпадает"


    return True, "Все слова соответствуют эталону"




@premium_router.message(F.text == '🧊')
async def send_request_for_access(message: Message) -> None:
    user_id = message.from_user.id
    w1 = ['President', 'Trump', 'broke', 'norms', 'when', 'he', 'delivered', 'a', 'rare', 'campaign', 'like', 'speech', 'at', 'the', 'Justice', 'Department', 'before', 'flying', 'to', 'Florida.', 'He', 'railed', 'against', 'the', 'judges,', 'prosecutors', 'and', 'others', 'who', 'conducted', 'criminal', 'investigations', 'of', 'him', 'during', 'Joe', "Biden's", 'presidency.', 'Scott', 'McFarlane', 'was', 'there.', 'President', 'Trump', 'stood', 'inside', 'the', 'headquarters', 'of', 'the', 'U.', 'S.', 'Justice', 'Department,', 'demonstrating', "he's", 'now', 'in', 'charge', 'and', 'promised', 'a', 'tougher', 'era', 'of', 'law', 'and', 'order.', 'Now', 'as', 'the', 'chief', 'law', 'enforcement', 'officer', 'in', 'our', 'country,', 'I', 'will', 'insist', 'upon', 'and', 'demand', 'full', 'and', 'complete', 'accountability', 'for', 'the', 'wrongs', 'and', 'abuses', 'that', 'have', 'occurred.', 'Trump', 'attacked', 'former', 'officials', 'and', 'prosecutors', 'at', 'the', 'Department', 'of', 'Justice', 'that', 'he', 'claimed', 'carried', 'out', 'corrupt', 'criminal', 'cases', 'against', 'him.', 'The', 'Justice', 'Department', 'and', 'the', 'FBI', 'have', 'long', 'prided', 'themselves', 'on', 'independence', 'from', 'the', 'White', 'House.', 'According', 'to', 'President', 'George', 'W.', 'Bush', 'administration,', 'Department', 'of', 'Justice', 'Tom', 'Dupree.', "He's", 'going', 'to', 'exercise', 'stronger', 'oversight', 'and', 'his', 'decision', 'to', 'go', 'from', 'the', 'White', 'House', 'to', 'the', 'Justice', 'Department', 'to', 'deliver', 'that', 'message', 'in', 'person', 'is', 'possibly', 'the', 'clearest', 'possible', 'way', 'he', 'could', 'underscore', 'his', 'point.', "Trump's", 'speech', 'comes', 'amid', 'a', 'purge', "that's", 'accelerating', 'inside', 'the', 'department.', 'Prosecutors', 'who', 'handled', 'January', '6', 'cases', 'and', 'the', 'investigations', 'of', 'Trump', 'have', 'been', 'fired', 'and', 'longtime', 'career', 'civil', 'servants', 'were', 'forced', 'to', 'retire,', 'including', 'the', 'head', 'of', 'the', 'FBI', 'field', 'office', 'in', 'New', 'York,', 'who', 'departed', 'amid', 'tears', 'and', 'ovations', 'from', 'longtime', 'colleagues.', "It's", 'shocking.', "It's", 'unprecedented.', 'Stacey', 'Young,', 'an', '18', 'year', 'veteran', 'who', 'resigned', 'in', 'January,', 'says', 'her', 'fellow', 'civil', 'servants', 'and', 'Department', 'of', 'Justice', 'offices', 'nationwide', 'face', 'retribution', 'for', 'handling', 'cases', 'Trump', 'allies', "don't", 'like.', 'These', 'are', 'the', 'people', 'who', 'keep', 'our', 'community', 'safe', 'and', 'our', 'nation', 'secure.', 'In', 'that', 'case,', 'why', 'are', 'they', 'gone', 'now?', "They're", 'gone', 'because', 'they', 'have', 'been', 'described', 'by', 'this', 'administration', 'as', 'political', 'operatives,', 'as', 'members', 'of', 'this', 'fictional', 'deep', 'state,', 'as', 'people', 'who', 'are', 'somehow', 'opposed', 'to', 'this', 'particular', 'president.', 'That', 'is', 'absolutely', 'not', 'the', 'case.', 'Among', 'those', 'in', 'the', 'front', 'row', 'for', "Trump's", 'remarks,', 'his', 'newly', 'appointed', 'and', 'confirmed', 'top', 'brass', 'at', 'the', 'Department', 'of', 'Justice,', 'the', 'FBI', 'Director', 'Kash', 'Patel', 'and', 'the', 'Deputy', 'Attorney', 'General', 'Todd', 'Blanche,', 'who', 'at', 'one', 'point', 'was', "Trump's", 'defense', 'lawyer', 'in', 'his', 'Manhattan', 'hush', 'money', 'case.', 'For', 'CBS', 'Saturday', 'Morning,', 'Scott', 'McFarlane,', 'Washington.']

    # добавьте остальные слова здесь
    new_segments = []
    text = " ".join(w1)
    from textblob import TextBlob

    blob = TextBlob(text)
    sentences = blob.raw_sentences
    settings = """You are given a sentence, divide it into meaningful sentences of 6-9 words. Keep all the words.
You cannot allow 1 word to be in a new line!!
in no case should you skip words, even insignificant ones like: and
Your answer should contain only new fragments of 6-9 words
fragment
fragment
fragment
...
so that your answer consists only of the words you received"""

    answer = await chunks_request(sentences, message, settings)
    for i in range(len(answer[1])):

        def merge_single_word_lines(asd):
            lines = asd.split("\n")  # Разбиваем текст на строки
            merged_lines = []

            for line in lines:
                if line.strip():  # Пропускаем пустые строки
                    if len(line.split()) == 1 and merged_lines:
                        merged_lines[-1] += " " + line.strip()  # Склеиваем с предыдущей строкой
                    else:
                        merged_lines.append(line.strip())  # Добавляем новую строку

            return "\n".join(merged_lines)
        r = merge_single_word_lines(answer[1][i])

        check = (compare_texts(r, sentences[i]))
        if check[0]:
            new_segments.append(r.split('\n'))
        else:
            print(f'error in {check}')
            error_ans = settings
            new_text = await solo_request(text=sentences[i], message=message, degree=0, settings=error_ans)
            r = merge_single_word_lines(new_text[1])
            check = (compare_texts(r, sentences[i]))
            if check[0]==False:
                do_split



        check = (compare_texts(r, sentences[i]))
        print(r)
        print('=')
        print(sentences[i])
        print('=')
        print(check)
        print('------------')

@premium_router.message(F.text == '🙏 Доступ')
async def send_request_for_access(message: Message) -> None:
    user_id = message.from_user.id
    is_user_exist_value = await db.is_user_exist(user_id)
    if is_user_exist_value:
        markup = CustomKeyboard.create_reply_main_menu()
        await message.answer(f"🧊 <b>{message.from_user.full_name} у Вас есть доступ!</b> 🧊", reply_markup=markup)
        return
    else:
        reply = CustomKeyboard.create_acsess().as_markup()
        if str(user_id) in admins_ids:
            await db.add_new_user(user_id)
            markup = CustomKeyboard.create_reply_main_menu()
            await bot.send_message(chat_id=user_id, text='Вам выдали доступ!', reply_markup=markup)
            return
        await bot.send_message(chat_id=admins_ids, text=f'Запросили доступ! \nid:{message.from_user.id} \nname:{message.from_user.full_name}', reply_markup=reply)



@premium_router.callback_query(F.data == '✅ Принять')
async def accept_new_user(callback_query: CallbackQuery, state: FSMContext) -> None:
    await callback_query.answer('Введите id:')
    await state.set_state(WaitingPremium.new_premium_id)


@premium_router.message(WaitingPremium.new_premium_id)
async def add_new_premium_user(message: Message, state: FSMContext):
    await db.add_new_user(message.text)
    markup = CustomKeyboard.create_reply_main_menu()
    await state.clear()
    for admin_id in admins_ids:
        await bot.send_message(text='Пользователь добавлен', chat_id=admin_id)
    await bot.send_message(chat_id=message.text, text='Вам выдали доступ!', reply_markup=markup)
