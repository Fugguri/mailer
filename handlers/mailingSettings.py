from main import bot
from aiogram import types
from main import dp, logger, db
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.keys import mailing_settings_kb, start, back
from utils import qlog, mlog
from pyrogram import Client
from main import scheduler
import asyncio
from pyrogram.errors.exceptions.flood_420 import *
from pyrogram.errors.exceptions.not_acceptable_406 import *
import sqlite3
from apscheduler.jobstores.base import ConflictingIdError
from pyrogram.errors.exceptions.bad_request_400 import *
from pyrogram.errors.exceptions.flood_420 import *
from pyrogram.errors.exceptions.forbidden_403 import *
from mailing import connect_and_send, sending_messages


class MailingSettings(StatesGroup):
    timeInterval = State()
    spamText = State()


user_client = {}


@dp.callback_query_handler(lambda call: call.data == "back")
@dp.callback_query_handler(lambda call: call.data == "Управление рассылкой", state="*")
async def mailSettings(callback: types.CallbackQuery, state: State):
    try:
        await state.finish()
    except:
        pass
    text = """Внимание, тут производится настройка рассылки.
Выберите номер, который хотите настроить"""
    phones = db.all_user_clients(callback.from_user.id)
    reply_markup = types.InlineKeyboardMarkup()
    for phone in phones:
        reply_markup.add(types.InlineKeyboardButton(
            text=phone, callback_data=phone))
    await qlog(callback, text, reply_markup)


@dp.callback_query_handler(lambda call: call.data in db.all_user_clients(call.from_user.id))
async def set_phone(callback: types.CallbackQuery):
    print(callback.data)
    user_client[callback.from_user.id] = callback.data
    text = "Выберите раздел для настройки"
    reply_markup = mailing_settings_kb()
    await qlog(callback, text, reply_markup)


@dp.callback_query_handler(lambda call: call.data == "Временной интервал")
async def setTimeInterval(callback: types.CallbackQuery):
    text = "Введите число (единицы измерения  - часы)\n1 - каждый час \n2 - каждые 2 часа \nи т.д."
    reply_markup = None
    await MailingSettings.timeInterval.set()
    await qlog(callback, text, reply_markup)


@dp.message_handler(state=MailingSettings.timeInterval)
async def updateTimeInterval(message: types.Message, state=State):
    text = f"""Временной промежуток между рассылками:{message.text}"""
    reply_markup = mailing_settings_kb()
    await state.finish()
    telegram_id = message.from_id
    client_number = user_client[message.from_id]
    interval = message.text
    db.edit_mailing_interval(client_number, interval)
    await mlog(message, text, reply_markup)


@dp.callback_query_handler(lambda call: call.data == "Текст рассылки")
async def setSpamText(callback: types.CallbackQuery):
    text = "Отправьте текст рассылки сообщением."
    reply_markup = None
    await MailingSettings.spamText.set()
    await qlog(callback, text, reply_markup)


@dp.message_handler(state=MailingSettings.spamText)
async def updateTimeInterval(message: types.Message, state=State):
    text = f"""Текст рассылки:{message.text}"""
    reply_markup = mailing_settings_kb()
    await state.finish()
    telegram_id = message.from_id
    client_number = user_client[message.from_id]
    text = message.text
    db.edit_mail_text(client_number, text)
    await mlog(message, text, reply_markup)


@dp.callback_query_handler(lambda call: call.data == "Подтвердить настройки")
async def acceptMailingSettings(callback: types.CallbackQuery):
    client_number = user_client[callback.from_user.id]
    client = db.get_data_for_client(client_number)
    client_id = client[0]
    api_id = client[2]
    api_hash = client[3]
    phone = client[4]
    mail_text = client[5]
    is_active = client[6]
    mailing_interval = client[7]
    chats = db.mailing_chats(client_id)
    if is_active:
        try:
            scheduler.add_job(connect_and_send,
                              trigger='interval',
                              name=phone,
                              id=phone,
                              hours=mailing_interval,
                              #   minutes=1,
                              args=(phone, api_id, api_hash, chats, mail_text, callback.from_user.id))
            db.client_on(client_number)
            try:
                scheduler.start()
            except:
                pass
            text = f"Успешно добавлено расписание для номера {phone}"
            reply_markup = back()
            await qlog(callback, text, reply_markup)

        except sqlite3.ProgrammingError:
            pass
        except ConflictingIdError:
            text = f"Автоматическая рассылка для номера {phone} уже запущена"
            reply_markup = back()
            await qlog(callback, text, reply_markup)
        except Exception as ex:
            print(ex)
            text = f"Ошибка {ex} Обратитесь к администратору"
            reply_markup = back()
            await qlog(callback, text, reply_markup)
    else:
        text = f"Оплатите доступ для номера {phone}"
        reply_markup = back()
        await qlog(callback, text, reply_markup)


@dp.callback_query_handler(lambda call: call.data == "Остановить рассылку")
async def stop_mailing(callback: types.CallbackQuery):
    try:
        client_number = user_client[callback.from_user.id]
        scheduler.remove_job(client_number)
        db.client_off(client_number)
        text = "Остановлено {}".format(client_number)
        reply_markup = back()
        await qlog(callback, text, reply_markup)
    except Exception as ex:
        text = "Ошибка {}".format(ex)
        reply_markup = back()
        await qlog(callback, text, reply_markup)


@dp.callback_query_handler(lambda call: call.data == "Собрать статистику")
async def stat(callback: types.CallbackQuery):
    reply_markup = back()
    try:
        client_number = user_client[callback.from_user.id]
        try:
            with open(f"mailing_data/{client_number}.txt", "r") as file:
                await callback.message.answer_document(file, caption=f"Данные обо всех отправленных сообщениях с номера {client_number}", reply_markup=reply_markup)
            return
        except:
            await qlog(callback, "Нет данных для этой рассылки", reply_markup)
            return
    except KeyError:
        text = "Нет данных для этой рассылки"
        reply_markup = back()
        await qlog(callback, text, reply_markup)
    except Exception as ex:
        print(ex)
        text = "Ошибка {}".format(ex)
        reply_markup = back()
        await qlog(callback, text, reply_markup)


@dp.callback_query_handler(lambda call: call.data == "Ручной запуск рассылки")
async def handleStartMaling(callback: types.CallbackQuery):
    client_number = user_client[callback.from_user.id]
    client = db.get_client_by_phone(client_number)
    client_id = client[0]
    user_id = client[1]
    api_id = client[2]
    api_hash = client[3]
    phone = client[4]
    mail_text = client[5]
    is_active = client[6]
    if is_active:
        chats = db.mailing_chats(client_id)
        if chats != ():
            # try:
                text = "Запускаю рассылку"
                reply_markup = mailing_settings_kb()
                await qlog(callback, text, reply_markup)
                await connect_and_send(phone, api_id, api_hash, chats, mail_text, callback.from_user.id)
                await asyncio.sleep(10)
            # except Exception as ex:
            #     text = f"Error {ex}. Обратитесь к администратору"
            #     reply_markup = back()
            #     await qlog(callback, text, reply_markup)
            #     print(ex)
        else:
            text = f"Сначала добавьте чаты"
            reply_markup = back()
            await qlog(callback, text, reply_markup)
    else:
        text = f"Оплатите доступ для номера {phone}"
        reply_markup = back()
        await qlog(callback, text, reply_markup)


@dp.callback_query_handler(lambda call: call.data == "back")
async def back_to_main(callback: types.CallbackQuery):
    text = "Вы в главном меню"
    reply_markup = start()
    await qlog(callback, text, reply_markup)


@dp.callback_query_handler(lambda call: call.data == "Назад в главное меню")
async def back_to_main(callback: types.CallbackQuery):
    text = "Вы в главном меню"
    reply_markup = start()
    await qlog(callback, text, reply_markup)
