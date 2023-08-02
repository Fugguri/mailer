from main import dp, db
from aiogram.dispatcher.filters.state import State, StatesGroup
# from keyboards import start_keyboard, keywords_list, unexcept_keywords_list, words_list, back, chats_list_, chats_key
from aiogram.dispatcher.filters import Text
from aiogram import types
from datetime import date
import datetime
import calendar
import keyboards


class Admin(StatesGroup):
    ferify = State()
    menu = State()
    activate = State()
    deactivate = State()
    add_admin = State()


admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
admin_markup.add(types.KeyboardButton(
    text="Активировать номер"))
admin_markup.add(types.KeyboardButton(
    text="Деактивировать номер"))
admin_markup.add(types.KeyboardButton(
    text="Добавить администратора"))
# admin_markup.add(types.KeyboardButton(
#     text="Отчет"))
admin_markup.add(types.KeyboardButton(
    text="Назад"))

back_key = types.ReplyKeyboardMarkup(resize_keyboard=True)
back_key.add(types.KeyboardButton(
    text="В меню"))


@ dp.message_handler(commands=["admin"])
async def admin_cab(message: types.Message):
    if message.from_user.username in ["fugguri", 'son2421'] or message.from_user.username in db.is_admin(message.from_user.username):
        await message.answer("Выберите команду", reply_markup=admin_markup)
        await Admin.menu.set()
    else:
        await Admin.ferify.set()
        await message.answer(text="Введите пароль администратора")


@ dp.message_handler(Text(equals="Назад"), state=Admin.menu)
async def admin_add(message: types.Message, state: State):
    reply_text = "Удалил клавиатуру админки"
    await message.reply(reply_text, reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Вы в главном меню", reply_markup=keyboards.start())
    await state.finish()


@ dp.message_handler(Text(equals="Назад"), state=Admin)
async def admin_add(message: types.Message, state: State):
    await message.answer("Вы в главном меню", reply_markup=keyboards.start())
    await state.finish()


@ dp.message_handler(Text(equals="Активировать номер"), state=Admin.menu)
async def back(message: types.Message, state: State):
    await message.answer(
        "Введите номер, который хотите активировать", reply_markup=back_key)
    await Admin.activate.set()


@ dp.message_handler(Text(equals="Деактивировать номер"), state=Admin.menu)
async def back(message: types.Message, state: State):
    await message.answer(
        "Введите номер, который хотите деактивировать", reply_markup=back_key)
    await Admin.deactivate.set()


@ dp.message_handler(Text(equals="Добавить администратора"), state=Admin.menu)
async def back(message: types.Message, state: State):
    await message.answer(
        "Введите ник(username) пользователя", reply_markup=back_key)
    await Admin.add_admin.set()


@ dp.message_handler(Text(equals="В меню"), state=Admin)
async def admin_add(message: types.Message, state: State):
    await state.finish()
    await message.answer("Выберите команду", reply_markup=admin_markup)
    await Admin.menu.set()


@ dp.message_handler(state=Admin.ferify)
async def is_correct(message: types.Message):
    if message.text == "SWMAdmin":
        await message.answer("Выберите команду", reply_markup=admin_markup)
        await Admin.menu.set()
    else:
        await message.answer("Неверно!\nПопробуйте еще раз")


@ dp.message_handler(state=Admin.add_admin)
async def back(message: types.CallbackQuery):
    if message.from_user.username in ["fugguri", 'son2421'] or message.from_user.username in db.is_admin(message.from_user.username):
        admin = str(message.text)
        db.add_admin(admin)
        await message.answer("Успешно")
    else:
        await message.answer("Вы не администратор")


@ dp.message_handler(state=Admin.activate)
async def activ(message: types.CallbackQuery):
    try:
        db.activate_client(message.text)
        await message.answer("Успешно!")
    except:
        await message.answer(
            "Ошибка!\nПроверьте данные или обратитесь к администратору!")


@ dp.message_handler(state=Admin.deactivate)
async def deactiv(message: types.Message):
    try:
        db.deactivate_client(message.text)
        await message.answer("Успешно!")
    except:
        await message.answer("Ошибка!\nПроверьте данные или обратитесь к администратору!")


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)
