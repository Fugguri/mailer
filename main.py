import logging
import json
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import openai
from DB_connectors.MySql_connect import Database
from apscheduler.schedulers.asyncio import AsyncIOScheduler


file = open("config.json", "r")
config = json.load(file)


TOKEN_API = config["TOKEN_API"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(f"logs/{__name__}.log", mode='w')
logger.addHandler(py_handler)



storage = MemoryStorage()
bot = Bot(TOKEN_API, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
db = Database("mailer")
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


async def on_startup(_):
    from mailing import start_mailing
    print("Бот запущен")
    logger.debug("Запущен бот!")
    db.cbdt()
    scheduler.start()
    clients = db.get_active_clients()
    for client in clients:
        await start_mailing(client[4])


async def on_shutdown(_):
    print("Бот остановлен")


if __name__ == "__main__":

    from handlers import dp
    executor.start_polling(
        dispatcher=dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )
