from aiogram import types
from main import dp, logger, db
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards
from aiogram import types
# from trash.telethon import TelegramClient
from threading import Thread
import asyncio


class EditBot(StatesGroup):
    scenario = State()
    scenario_system = State()
    scenario_assistant = State()


kb = keyboards.back()
phone = {}


@dp.callback_query_handler(lambda call: call.data == "Редактировать бота")
async def start(callback: types.CallbackQuery):
    logger.info(f'{callback.from_user}  - Редактировать бота')
    await EditBot.scenario.set()
    text = """Выберите номер, к которому хотите привязать новый сценарий"""
    nums = db.all_user_bots(callback.from_user.id)
    for num in nums:
        kb.add(types.InlineKeyboardButton(
            text=num, callback_data=num))
    await callback.message.answer(text=text, reply_markup=kb, disable_web_page_preview=True)


@ dp.callback_query_handler(lambda call: call.data == "back", state=EditBot)
async def back_to_main_menu(callback: types.CallbackQuery, state=State):
    await state.finish()
    logger.info(f'{callback.from_user}  - back')
    await callback.message.answer(text="Вы в главном меню!", reply_markup=keyboards.start())


@dp.callback_query_handler(state=EditBot.scenario)
async def select_phone(callback: types.callback_query):
    phone[callback.from_user.id] = callback.data
    await EditBot.scenario_system.set()
    text = """<b>Опишите задачи, которые стоят перед ботом.</b>\n
<u>Системные настройки</u>: - То, какие задачи будет выполнять бот. В этот момент можно вписать описании компании и контент который бот будет выдавать в зависимости от контекста.\n
Пример описания системной роли:\n Ты бот - менеджер по продажам, строительной кампании, тебя зовут Дарья.
Обьекты недвижимости можно посмотреть по ссылке:  https://www.lsr.ru/
Наши соц сети: https://tg.me/fugguri\n
Наши акции: Приведи друга - скидка на 10%
Рассрочка: вы можете оформить рассрочку 0/0/24 с первоначальным взносом в 30 % от стоимости(это не актуальное предложение)
__________________________\n"""
    await callback.message.answer(text=text, reply_markup=kb)


@dp.message_handler(state=EditBot.scenario_system)
async def create_scenario(message: types.Message):
    db.update_description(phone[message.from_user.id], message.text)
    await message.answer(message.text, reply_markup=kb)


@ dp.message_handler(lambda mes: mes.text == "Далее", state=EditBot.scenario)
async def update_scenario(message: types.Message):
    numbers = db.all_user_bots(message.from_id)
    await message.answer("Выберите профиль {}".format(numbers), reply_markup=kb)
