from aiogram import types
from main import dp, logger


@dp.callback_query_handler(lambda call: call.data == "Оплата")
async def start(callback: types.CallbackQuery):
    logger.info(f'{callback.from_user}  - оплата')
    await callback.message.answer(text="Для получения доступа\nНапишите @son2421")
