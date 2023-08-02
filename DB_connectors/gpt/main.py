from aiogram import Bot, Dispatcher, executor, types
import openai
import json
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging
openai.api_key = "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"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file = open("config.json", "r")
config = json.load(file)

OPENAI_KEY = config["openai"]
TOKEN_API = config["TOKEN_API"]


messages = [
    {'role': "system",
     "content": """Ты девушка Алиса Алиса, 20 лет, занимаешься фитнесом, любишь животных.Любишь общаться 
     """},
    {'role': "user", "content": "хочет получить контент от модели, возможно какую-то скидку на контент, доброе комплиментарное общение, создание иллюзии, что он особенный для модели, возможно оценку своего тела"},
    {'role': "assistant", "content": " Ты приветствуешь пользователя один раз какой нибудь милой шуткой у тебя романтично-комплиментарный стиль общения"},

]

users_message = {}


def update(user, message, role, content):
    try:
        users_message[user].append({"role": role, "content": content})
    except:
        users_message[user] = messages
    return users_message[user]


storage = MemoryStorage()
bot = Bot(TOKEN_API, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
# db = Database("TopLid")
py_handler = logging.FileHandler(f"{__name__}.log", mode='w')
logger.addHandler(py_handler)


async def on_startup(_):
    print("Бот запущен")
    logger.debug("Запущен бот!")


async def on_shutdown(_):
    print("Бот остановлен")


@dp.message_handler()
async def asd(message: types.Message):
    update(message.from_id, messages, "user", message.text)
    responce = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=users_message[message.from_id]
    )
    print(responce)
    logger.info(
        f"{message.from_user}: {message.text}\n{responce['choices'][0]['message']['content']}")

    await message.answer(responce['choices'][0]['message']['content'])


if __name__ == "__main__":
    from handlers import dp
    executor.start_polling(
        dispatcher=dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    )
