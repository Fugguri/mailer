import openai
from telethon import TelegramClient, events
from main import dp, bot
from aiogram import types
from main import dp, logger, db
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards
from aiogram import types
# from trash.telethon import TelegramClient
from threading import Thread
import asyncio
kb = keyboards.back().add(types.InlineKeyboardButton(
    text="Далее", callback_data="Далее"))


class StartBot(StatesGroup):
    scenario = State()
    scenario_system = State()
    scenario_assistant = State()


kb = keyboards.back()
phone = {}


@dp.callback_query_handler(lambda call: call.data == "Запуск бота")
async def start(callback: types.CallbackQuery):
    logger.info(f'{callback.from_user.id}  - Редактировать бота')
    await StartBot.scenario.set()
    text = """Выберите номер, к которому хотите привязать новый сценарий"""
    nums = db.all_user_bots(callback.from_user.id)
    for num in nums:
        kb.add(types.InlineKeyboardButton(
            text=num, callback_data=num))
    await callback.message.answer(text=text, reply_markup=kb, disable_web_page_preview=True)


@ dp.callback_query_handler(lambda call: call.data == "back", state=StartBot)
async def back_to_main_menu(callback: types.CallbackQuery, state=State):
    await state.finish()
    logger.info(f'{callback.from_user}  - back')
    await callback.message.answer(text="Вы в главном меню!", reply_markup=keyboards.start())


@dp.callback_query_handler(state=StartBot.scenario)
async def select_phone(callback: types.callback_query):
    # phone[callback.from_user.id] = callback.data
    a = db.get_data_for_client(callback.data)
    api_id = a[2]
    api_hash = a[3]
    phone = a[4]
    settings = a[5]
    client = TelegramClient("sessions/"+phone, api_id, api_hash)

    try:
        await callback.message.answer(f"Запустил бота {phone.replace('sessions/','')}", reply_markup=kb)
        await main(client)
    except Exception as ex:
        print(ex)
        await callback.message.answer("Ошибка бота {} обратитеть в поддержку".format(phone))

users_message = {}


async def my_event_handler(event):
    me = await event.client.get_me()
    phone = "+" + me.phone
    settings = db.get_data_for_client(phone)[5]

    try:
        users_message[event.chat_id]
    except:
        db.start_new_dialog_counter_update(phone)
        messages = [
            {'role': "system", "content": settings},
        ]
        users_message[event.chat_id] = messages
        db.start_new_dialog_counter_update(phone)

    if users_message[event.chat_id][0]["content"] != settings:
        messages = [
            {'role': "system", "content": settings},
        ]
        users_message[event.chat_id] = messages

    users_message[event.chat_id].append(
        {"role": "user", "content": event.text})
    responce = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=users_message[event.chat_id]
    )
    sender = await event.get_sender()
    answer = responce['choices'][0]['message']['content']
    users_message[event.chat_id].append(
        {"role": "assistant", "content": answer})
    await event.client.send_message(message=answer, entity=sender)


async def main(client):
    async with client:
        me = await client.get_me()
        print('Working with', me.first_name, me.last_name)
        await client.start()
        client.add_event_handler(my_event_handler, events.NewMessage)
        await client.run_until_disconnected()
