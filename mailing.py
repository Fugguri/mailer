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
                              misfire_grace_time = 1000,
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


async def connect_and_send(phone, api_id, api_hash, chats, mail_text, telegram_id):
    try:
        async with Client(phone, api_id=api_id, api_hash=api_hash,
                          phone_number=phone, workdir="sessions/") as app:
            
            sending_messages[phone] = []
            for chat in chats:
                try:
                    message = await app.send_message(chat[3], mail_text)
                    sending_messages[phone].append(datetime.datetime.now().strftime("%D %H:%M ") + "MSK "
                                                   f"t.me/{message.chat.username}/{message.id}")
                    with open(f"mailing_data/{phone}.txt","a") as file:
                        file.write(datetime.datetime.now().strftime("%d.%m.%Y %H:%M ") + "MSK "+f"t.me/{message.chat.username}/{message.id} \n")
                    await asyncio.sleep(15)
                    print(phone)
                except errors.exceptions.not_acceptable_406.ChannelPrivate as ex:
                    await bot.send_message(telegram_id, f"Это приватный канал {chat}, невозможно отправить сообщение")
                    continue
                except Forbidden:
                    await bot.send_message(telegram_id, "Вы не можете отправлять мультимедийные (текстовые) сообщения в этом чате. чат - {}  Номер телефона - {}".format(chat, phone))
                    continue
                except UserBannedInChannel:
                    await bot.send_message(telegram_id, "Вы больше не можете отправлять сообщения вгруппы и каналы с номера {} для получения дополнительной информации перейдите в @SpamBot".format(phone))
                    return
                except UserDeactivatedBan:
                    await bot.send_message(telegram_id, "Ваш номер был заблокирован {}.".format(phone))
                    scheduler.remove_job(phone)
                    db.deactivate_client(phone)
                    return
                except BotBlocked:
                    return
                except errors.exceptions.forbidden_403.ChatAdminRequired:
                    pass
                except AttributeError:
                    print(phone)
                    pass
                except Exception as ex:
                    print(ex, phone)
                    
                    continue
    except UserDeactivatedBan:
        await bot.send_message(telegram_id, "Ваш номер был заблокирован {}.".format(phone))
        scheduler.remove_job(phone)
        db.deactivate_client(phone)
        return
    except BotBlocked:
        return
    except Exception as ex:
        print(ex, phone)
