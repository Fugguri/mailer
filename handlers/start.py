from aiogram import types
from main import dp, bot, logger, db
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards
import datetime


class AddWord(StatesGroup):
    word = State()


@dp.message_handler(commands='start', state="*")
async def start(message: types.Message,state:State):
    start_date = datetime.date.today()  # год, месяц, число
    result_date = start_date - datetime.timedelta(days=1)
    telegram_id = message.from_user.id
    logger.info(f'{message.from_user, message.text}')
    await message.answer("Добро пожаловать!", reply_markup=keyboards.start())
    db.create_user(
        telegram_id,
        message.from_user.full_name,
        message.from_user.username,
        str(result_date)
    )
    try:
        await state.finish()
    except: 
        pass
