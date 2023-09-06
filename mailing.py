from pyrogram import Client
from pyrogram import errors
import asyncio
import sqlite3
import datetime
from utils import db
from main import scheduler, bot, db
from apscheduler.jobstores.base import ConflictingIdError

from aiogram.utils.exceptions import BotBlocked
from pyrogram.errors.exceptions.not_acceptable_406 import *
from pyrogram.errors.exceptions.bad_request_400 import *
from pyrogram.errors.exceptions.flood_420 import *
from pyrogram.errors.exceptions.forbidden_403 import *
from pyrogram.errors.exceptions.unauthorized_401 import *
sending_messages = {}


async def mail_to_list_of_ids(*args, **kwargs):
    receivers = ()
    phone = ""
    api_id = ""
    api_hash = ""
    message_text = ""
    timeout = 30
    client = Client(phone, api_id=api_id, api_hash=api_hash,
                    phone_number=phone, workdir="sessions/")
    async with client as client:
        for receiver in receivers:
            await client.send_message(chat_id=receiver, text=message_text)
            await asyncio.sleep(timeout)


async def start_mailing(client_number):
    client = db.get_data_for_client(client_number)
    client_id = client[0]

    api_id = client[2]
    api_hash = client[3]
    phone = client[4]
    mail_text = client[5]
    is_active = client[6]
    is_working = client[8]
    mailing_interval = client[7]
    chats = db.mailing_chats(client_id)
    if is_working and is_active:
        try:
            scheduler.add_job(connect_and_send,
                              trigger='interval',
                              name=phone,
                              id=phone,
                              hours=mailing_interval,
                              #   minutes=1,
                              misfire_grace_time=1000,
                              args=(phone, api_id, api_hash, chats, mail_text, client[-4]))

            pass
            print(f"mailing settings approve for {client_number}")
        except UserDeactivatedBan:
            # await bot.send_message(telegram_id, "Ваш номер был заблокирован {}.".format(phone))
            scheduler.remove_job(phone)
            db.deactivate_client(phone)
            return
        except sqlite3.ProgrammingError:
            pass
        except Exception as ex:
            print(ex)
        try:
            scheduler.start()
        except:
            pass


def write_mailing_data(phone, message):
    date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M ") + "MSK "
    msg = f"t.me/{message.chat.username}/{message.id} \n"
    with open(f"mailing_data/{phone}.txt", "a") as file:
        file.write(date + msg)


def write_mailing_err_data(phone, err=None, chat=None):
    date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M ") + "MSK "
    with open(f"mailing_data/{phone}.txt", "a") as file:
        file.write(date + chat+" "+err)


async def connect_and_send(phone, api_id, api_hash, chats, mail_text, telegram_id):
    proxy = {"scheme": "HTTPS", "hostname": "45.92.171.19",
             "port": 8000, "login": 'dGC5o8', "password": 'zcf7tx'}
    # try:
    async with Client(phone, api_id=api_id, api_hash=api_hash,
                      phone_number=phone, workdir="mailing_sessions/") as app:
        sending_messages[phone] = []
        print(len(chats))
        return
        for chat in chats:
            try:
                message = await app.send_message(chat[3], mail_text)
                sending_messages[phone].append(datetime.datetime.now().strftime("%D %H:%M ") + "MSK "
                                               f"t.me/{message.chat.username}/{message.id}")
                write_mailing_data(phone, message)
                await asyncio.sleep(15)
            except UserBannedInChannel:
                text = "Вы больше не можете отправлять сообщения в группы и каналы с номера {} для получения дополнительной информации перейдите в @SpamBot".format(
                    phone)
                await bot.send_message(telegram_id, text)
                write_mailing_err_data(phone, message, err=text, chat=chat)
                return
            except errors.exceptions.not_acceptable_406.ChannelPrivate as ex:
                text = f"Это приватный канал {chat}, невозможно отправить сообщение"
                await bot.send_message(telegram_id, text)
                write_mailing_err_data(phone, err=text, chat=chat)
                continue
            except Forbidden:
                text = "Вы не можете отправлять мультимедийные (текстовые) сообщения в этом чате. чат - {}  Номер телефона - {}".format(
                    chat, phone)
                await bot.send_message(telegram_id, text)
                write_mailing_err_data(phone, err=text, chat=chat)
                continue
            except errors.exceptions.forbidden_403.ChatAdminRequired as ex:
                text = "у вас нет прав администратора, чтобы отправлять сообщения в этот чат/канал"
                await bot.send_message(telegram_id, text)
                write_mailing_err_data(phone, err=text, chat=chat)

            except UserDeactivatedBan:
                text = "Ваш номер был заблокирован {}.".format(phone)
                await bot.send_message(telegram_id, text)
                scheduler.remove_job(phone)
                write_mailing_err_data(phone, err=ex, chat=chat)
                db.deactivate_client(phone)
                return
            except AttributeError as ex:
                print(phone, ex)
                pass
            except Exception as ex:
                write_mailing_err_data(phone, err=ex, chat=chat)
                print(ex, phone)
                continue
            finally:
                print(sending_messages[phone])
    # except UserDeactivatedBan:
    #     await bot.send_message(telegram_id, "Ваш номер был заблокирован {}.".format(phone))
    #     scheduler.remove_job(phone)
    #     db.deactivate_client(phone)
    #     return
    # except BotBlocked:
    #     return
    # except Exception as ex:
    #     print(ex, phone)
