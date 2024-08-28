from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.states import WaitingStateGpt
from spawnbot import bot
from menu import keyboards
from handlers.gpt_handlers.gpt_file import process_file_gpt_request

QUEUE = []
gpt_file_queue = Router()
previous_message_id = None


@gpt_file_queue.message(F.text == '🗄 Очередь')
async def process_message_gpt_request(message: Message, state: FSMContext) -> None:
    global previous_message_id
    await state.clear()
    user_id = message.from_user.id
    QUEUE.clear()
    await state.set_state(WaitingStateGpt.queue_files)

    if previous_message_id:
        try:
            await bot.delete_message(user_id, previous_message_id)
        except Exception as e:
            print(e, 'in process_message_gpt_request (DELETE)')

    sent_message = await bot.send_message(user_id, '<b>Ожидается файл</b>')
    previous_message_id = sent_message.message_id


@gpt_file_queue.message(WaitingStateGpt.queue_files)
async def accept_file(message: Message) -> None:
    global previous_message_id
    user_id = message.from_user.id

    if previous_message_id:
        await bot.delete_message(user_id, previous_message_id)

    QUEUE.append([message, None])
    markup = keyboards.CustomKeyboard.create_queue_button().as_markup()
    sent_message = await bot.send_message(user_id, f'<b>Количество файлов:</b> {len(QUEUE)}', reply_markup=markup)
    previous_message_id = sent_message.message_id


@gpt_file_queue.callback_query(F.data == '✅ Выполнить')
async def use_default_settings(callback_query: CallbackQuery, state: FSMContext) -> None:
    for n in QUEUE:
        await process_file_gpt_request(n[0], state, n[1])
    await state.clear()