from spawnbot import bot
from config_reader import admins_ids
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from db.database import db
from aiogram.fsm.context import FSMContext
from states.states import WaitingPremium
from menu.keyboards import CustomKeyboard
from aiogram.types import Message, CallbackQuery


premium_router = Router()


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
        for admin_id in admins_ids:
            if str(user_id) in admins_ids:
                await db.add_new_user(user_id)
                markup = CustomKeyboard.create_reply_main_menu()
                await bot.send_message(chat_id=user_id, text='Вам выдали доступ!', reply_markup=markup)
                return
            await bot.send_message(chat_id=admin_id, text=f'Запросили доступ! \nid:{message.from_user.id} \nname:{message.from_user.full_name}', reply_markup=reply)



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
