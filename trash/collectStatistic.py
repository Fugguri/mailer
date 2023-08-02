from aiogram import types
from main import dp, logger, db
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards
from aiogram import types
from trash.telethon import TelegramClient
from threading import Thread
import asyncio


class Static(StatesGroup):
    counter = State()


kb = keyboards.back()
phone = {}


@dp.callback_query_handler(lambda call: call.data == "Собрать статистику")
async def start(callback: types.CallbackQuery):
    logger.info(f'{callback.from_user} - Собрать статистику')
    await Static.counter.set()
    text = """Выберите номер,с которого собираем статистику"""
    nums = db.all_user_bots(callback.from_user.id)
    for num in nums:
        kb.add(types.InlineKeyboardButton(
            text=num, callback_data=num))
    await callback.message.answer(text=text, reply_markup=kb, disable_web_page_preview=True)


@ dp.callback_query_handler(lambda call: call.data == "back", state=Static)
async def back_to_main_menu(callback: types.CallbackQuery, state=State):
    await state.finish()
    logger.info(f'{callback.from_user}  - back')
    await callback.message.answer(text="Вы в главном меню!", reply_markup=keyboards.start())


@dp.callback_query_handler(state=Static.counter)
async def create_scenario(call: types.CallbackQuery):
    counter = db.get_dialog_counter(call.data)[0]
    await call.message.answer(f"У профиля {call.data} - {counter} заявок", reply_markup=kb)


@ dp.message_handler(lambda mes: mes.text == "Далее", state=Static)
async def update_scenario(message: types.Message):
    numbers = db.all_user_bots(message.from_id)
    await message.answer("Выберите профиль {}".format(numbers), reply_markup=kb)
