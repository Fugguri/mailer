from aiogram import types
from main import dp, logger
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.keys import chatsList, back,start
from utils import qlog, mlog, clear_urls
from .mailingSettings import user_client
from pyrogram import Client
from utils import db
import asyncio
from pyrogram.errors.exceptions.bad_request_400 import *
from pyrogram.errors.exceptions.flood_420 import *
from pyrogram.errors.exceptions.forbidden_403 import *


class ChatsSettings(StatesGroup):
    addChats = State()


@dp.callback_query_handler(lambda call: call.data == "Чаты")
async def chatsSettings(callback: types.CallbackQuery):
    print(user_client[callback.from_user.id])
    chats = db.get_chats_list(user_client[callback.from_user.id],callback.from_user.id)
    print(chats)
    text = "Всего чатов - {}".format(len(chats))
    reply_markup = chatsList(chats)
    await qlog(callback, text, reply_markup)


@dp.callback_query_handler(lambda call: call.data == "back",state=ChatsSettings.addChats)
async def back_to_main(callback: types.CallbackQuery):
    text = "Вы в главном меню"
    reply_markup = start()
    await qlog(callback, text, reply_markup)

@dp.callback_query_handler(lambda call: call.data == "Добавить чат")
async def addChat(callback: types.CallbackQuery):
    await ChatsSettings.addChats.set()
    text = """Введите ссылку на чат или чаты.\n Формат ссылки "https://t.me/СсылкаНаЧат" """
    reply_markup = back()
    await qlog(callback, text, reply_markup)
    
    
@dp.message_handler(state=ChatsSettings.addChats)
async def updateTimeInterval(message: types.Message, state=State):
    if "https://t.me/" in message.text:
        chats_to_join = message.text.replace("\n", "").replace(
            ",", "").replace(" ", "").split("https://t.me/")
        text = f"""<b>Запускаю вступление в чаты, это может занять некоторое время.</b>
Чтобы избежать блокировок чаты подключаются по 4 чата с промежутком в 5 минут.
В случае возникновения ошибок вам придет сообщение"""
        phone = user_client[message.from_id]
        client_data = db.get_data_for_client(phone)
        api_id = client_data[2]
        api_hash = client_data[3]
        phone = client_data[4]
        existed_chats = db.client_chats(client_data[1])

        chats = db.client_chats(client_data[0])
        reply_markup = chatsList(chats)
        await mlog(message, text, reply_markup)
        await state.finish()
        # try:
        async with Client(phone, api_id=api_id, api_hash=api_hash,
                          phone_number=phone, workdir="sessions/") as app:
            counter = 0
            for chat in chats_to_join:
                if chat != "":
                    if chat not in existed_chats:
                        try:
                            if counter == 3:
                                await asyncio.sleep(300)
                                counter = 0
                            chat_data = await app.join_chat(chat.replace("https://t.me/", "").strip())
                            chats = db.add_chat(chat,
                                                chat_data.username,
                                                chat_data.id,
                                                client_data[0])
                            counter += 1

                        except KeyError as ex:
                            await message.answer("Чат не найден {}".format(chat))
                        except UsernameInvalid as ex:
                            await message.answer("Чат не найден {}".format(chat))
                        except UsernameNotOccupied as ex:
                            await message.answer("Чат не найден {}".format(chat))
                        except ChatAdminRequired as ex:
                            await message.answer("Нужны права администратора {}".format(chat))
                        except ChannelsTooMuch as ex:
                            await message.answer("У вас в профиле сликом много чатов, купите подписку Telegram Premium или загрузите новый профиль. Заканчиваю вступление.")
                            break
                        except FloodWait as ex:
                            await message.answer(f"Внимание, слишком ного попыток присоединения, придется подождать {ex.value} секунд.")
                            await asyncio.sleep(ex.value)
                        except Exception as ex:
                            await message.answer(f"Ошибка, обратитесь к администратору {ex}")
                            continue
                        finally:
                            await asyncio.sleep(3)
        chats = db.client_chats(client_data[0])
        text = "Закончил вступление в чаты"
        reply_markup = chatsList(chats)
        await mlog(message, text, reply_markup)

        # except Exception as ex:
        # await state.finish()
        # chats = db.client_chats(client_data[0])
        # # urls = await clear_url(message.text)
        # reply_markup = chatsList(chats)
        # await mlog(message, text, reply_markup)
    else:
        chats = db.get_chats_list(user_client[message.from_user.id],message.from_user.id)
        text = "В сообщении нет ни одной ссылки на чат.\nУбедитесь, что ввели корректную ссылку и попробуйте заново."
        reply_markup = chatsList(chats)
        await state.finish()
        await mlog(message, text, reply_markup)
