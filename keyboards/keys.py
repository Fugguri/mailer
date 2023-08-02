from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def inline():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="", callback_data=""))
    return kb


def keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text=""))
    return kb


def chatsList(chats):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="Добавить чат", callback_data="Добавить чат"))
    kb.add(InlineKeyboardButton(text="Назад", callback_data="back"))
    for i in chats:
        name = i[1].replace("https://t.me/", "")
        kb.add(InlineKeyboardButton(text=name, callback_data=name))
    return kb


def start():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        text="➕Добавить профиль➕", callback_data="Добавить профиль"))
    kb.add(InlineKeyboardButton(text="⚙️Управление рассылкой⚙️",
           callback_data="Управление рассылкой"))
    kb.add(InlineKeyboardButton(text="🆘Информация🆘", callback_data="Информация"))
    kb.add(InlineKeyboardButton(text="🪙Оплата🪙", callback_data="Оплата"))

    return kb


def mailing_settings_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="📅Временной интервал📅",
           callback_data="Временной интервал"))
    kb.add(InlineKeyboardButton(
        text="📝Текст рассылки📝",
        callback_data="Текст рассылки"))
    kb.add(InlineKeyboardButton(
        text="Настройка чатов и групп🗣",
        callback_data="Чаты"))
    kb.add(InlineKeyboardButton(
        text="✅Запустить рассылку ✅",
        callback_data="Подтвердить настройки"))
    kb.add(InlineKeyboardButton(
        text="Остановить рассылку",
        callback_data="Остановить рассылку"))
    kb.add(InlineKeyboardButton(
        text="✋Ручной запуск рассылки✋",
        callback_data="Ручной запуск рассылки"))
    kb.add(InlineKeyboardButton(
        text="Назад в главное меню",
        callback_data="Назад в главное меню"))
    kb.add(InlineKeyboardButton(
        text="Собрать статистику по последней рассылке",
        callback_data="Собрать статистику"))
    return kb


def back():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        text="Назад",
        callback_data="back"))
    return kb
