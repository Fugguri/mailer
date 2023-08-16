from aiogram import types
from main import dp, logger, db
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards
from aiogram import types
from pyrogram import Client
from threading import Thread


class AddProfile(StatesGroup):
    intro = State()
    client_data = State()
    connection = State()
    password = State()


thread = ""
client = []
users_data = {}
code_hash = ""
client = ""
kb = keyboards.back().add(types.InlineKeyboardButton(
    text="Далее", callback_data="Далее"))


@dp.callback_query_handler(lambda call: call.data == "Добавить профиль",state="*")
async def start(callback: types.CallbackQuery,state: State):
    logger.info(f'{callback.from_user}  - добавить профиль')
    await AddProfile.intro.set()
    users_data[callback.from_user.id] = {}
    await callback.message.answer(
        text="Ссылка на инструкцию по регистрации https://telegra.ph/Instrukciya-po-registracii-03-25 ", reply_markup=kb)
    try:
        await state.finish()
    except: 
        pass


@dp.callback_query_handler(lambda call: call.data == "Далее", state=AddProfile.intro)
async def next(callback: types.CallbackQuery):
    logger.info(
        f'{callback.from_user}  - Добавление бота - далее( после инструкции)')
    await AddProfile.client_data.set()
    await callback.message.answer(f"""Введите api_id, api_hash и номер телефона, который вы указывали при регистрации
\nФормат ввода данных 12345, 12312432sdcasf123213423, +7999999999 \nЧерез запятую в такой же постедовательности + у номера обязателен
\nЧтобы продолжить нажмите "далее" """, reply_markup=keyboards.back())


@dp.message_handler(state=AddProfile.client_data)
async def collect_id(message: types.Message):
    logger.info(f'{message.from_user}  - добавление client_data')
    try:
        api_id, api_hash, phone = message.text.replace(" ", "").split(",")
        users_data[message.from_user.id]["api_id"] = api_id
        users_data[message.from_user.id]["api_hash"] = api_hash
        users_data[message.from_user.id]["phone"] = phone
        await AddProfile.connection.set()
        await message.answer(f"Текущие данные: \napi_id: {api_id} ,\napi_hash: {api_hash} , \nphone: {phone} \nЧтобы продолжить нажмите далее", reply_markup=kb)
    except Exception as ex :
        print(ex)
        await message.answer(f"Ошибка в обработке данных, проверьте данные и попробуйте снова.", reply_markup=keyboards.back())


@dp.callback_query_handler(lambda call: call.data == "Далее", state=AddProfile.connection)
async def next_numver(callback: types.CallbackQuery):
    logger.info(
        f'{callback.from_user}  - connect')
    phone = users_data[callback.from_user.id]["phone"]
    api_id = users_data[callback.from_user.id]["api_id"]
    api_hash = users_data[callback.from_user.id]["api_hash"]

    client = users_data[callback.from_user.id]["client"] = Client(phone, api_id=api_id,
                                                                  api_hash=api_hash, phone_number=phone, workdir="sessions/")
    global code_hash
    try:
        await client.connect()
        send_code = await client.send_code(phone_number=phone)
        code_hash = send_code.phone_code_hash
        users_data[callback.from_user.id]["code_hash"] = send_code.phone_code_hash
        # await client.disconnect()
        await callback.message.answer("Код запрошен, введите код для входа", reply_markup=keyboards.back())
    except Exception as ex:
        await callback.message.answer(f"Ошибка {ex}", reply_markup=keyboards.back())


@dp.message_handler(state=AddProfile.connection)
async def next_number(message: types.Message):
    await message.answer("Запускаю")
    phone = users_data[message.from_user.id]["phone"]
    code_hash = users_data[message.from_user.id]["code_hash"]
    client = users_data[message.from_user.id]["client"]
    api_id = users_data[message.from_user.id]["api_id"]
    api_hash = users_data[message.from_user.id]["api_hash"]
    try:
        password = message.text.split(",")[1]
        """Допускаю возможность добавить двухфакторную авторизацию"""
    except:
        code = message.text.split(",")[0]
        try:
            # await client.connect()
            await client.sign_in(phone, code_hash, code)
            me = await client.get_me()
            await client.disconnect()
            await message.answer(f"Успешно {me.first_name} {me.last_name}", reply_markup=keyboards.back())
            db.create_client(message.from_id, api_id, api_hash, phone)
        except Exception as ex:
            await message.answer(f"Ошибка {ex}", reply_markup=keyboards.back())


@ dp.callback_query_handler(lambda call: call.data == "back", state=AddProfile)
async def back_to_main_menu(callback: types.CallbackQuery, state=State):
    await state.finish()
    logger.info(f'{callback.from_user}  - back')
    await callback.message.answer(text="Вы в главном меню!", reply_markup=keyboards.start())
