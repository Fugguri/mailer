from telethon import TelegramClient
from pymysql.err import IntegrityError
from telethon.errors.rpcerrorlist import InviteHashExpiredError, InviteRequestSentError, FloodWaitError, UserAlreadyParticipantError, ChannelsTooMuchError
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from asyncio import sleep
from main import logger, bot, db


async def qlog(callback, text, reply_markup=None):
    logger.info(f'{callback.from_user}  - {callback.data}')
    await callback.message.answer(text=text, reply_markup=reply_markup)


async def mlog(message, text, reply_markup=None):
    logger.info(f'{message.from_user}  - {message.text}')
    await message.answer(text=text, reply_markup=reply_markup)


async def clear_urls(urls):
    dirtyUrl = urls.split("https://t.me/")
    clear_urls = list(map(lambda x: x.replace("\n", "").replace(",", "").replace(
        " ", '').replace("+", "").replace('joinchat/', ""), dirtyUrl))
    return clear_urls[1:]


async def connectAndAddChat(telegram_id, message, urls):
    client_data = "DB CLIENT DATA"
    phone = client_data[0]
    api_id = client_data[1]
    api_hash = client_data[2]
    client_chats = "DB CLIENTSCHATS"
    client = TelegramClient(phone, api_id, api_hash)
    joined_group_count = 1
    for url in urls:
        if joined_group_count < 4:
            if url != "" and url not in client_chats:
                try:
                    async with client:
                        await join_chat(message, url, telegram_id, client, db)
                    joined_group_count += 1
                except FloodWaitError as ex:
                    sleep(ex.seconds)
                except ChannelsTooMuchError:
                    message.answer("Вы достигли лимита по группам")
                except Exception as ex:
                    logger.debug(f'{ex}, {telegram_id}, {message}')
                    message.answer(
                        f"Ошибка, {ex} Внимание! Сообщите администратору об этой ошибке, во избежание подобных ошибок в будущем.")
                finally:
                    logger.debug(f"done {url}")
            elif url != "" and url in client_chats:
                message.answer("Вы уже добавляли эту группу")
            async with client:
                await save(telegram_id, url, url, client, db)
        else:
            joined_group_count = 0
            logger.debug("Добавлено 4 чата! Тайм- аут 400 секунд")
            await sleep(400)

    message.answer("Все группы добавлены")


async def join_chat(url, telegram_id, client, db):
    clear_url = url
    try:
        logger.debug("try ChatInvite" + clear_url)
        await client(ImportChatInviteRequest(clear_url))
        await sleep(10)
        logger.debug("try save")
        await save(telegram_id, url, clear_url, client, db)
        logger.debug("Joined and save", url)
        return
    except InviteHashExpiredError as ex:
        try:
            logger.debug("try JoinChannel")
            entity = await client.get_entity(clear_url)
            await client(JoinChannelRequest(entity))
            logger.debug("try save")
            await save(telegram_id, url, clear_url, client, db)
            logger.debug(f"Joined and save, {url}")
            return
        except ValueError:
            logger.debug("Ссылка недействительна!")
            await bot.send_message(
                chat_id=telegram_id, text=f"Ссылка на чат {url} недействительна... Попробуйте другую")
            return
        except InviteRequestSentError as er:
            logger.debug(er)
            return
        except ChannelsTooMuchError:
            logger.debug("Ограничение по количеству групп " + url)
            await bot.send_message(chat_id=248184623, text=f"Ограничение по количеству групп {client}")
            return
    except InviteRequestSentError as er:
        logger.debug(str(er)+url)
        logger.debug("try save")
        await save(telegram_id, url, clear_url, client, db)
        logger.debug(f"Joined and save, {url}")
        return
    except ValueError:
        logger.debug("Ссылка недействительна!")
        await bot.send_message(
            chat_id=telegram_id, text=f"Что-то пошло не так {url}")
        return
    except ChannelsTooMuchError:
        logger.debug("Ограничение количества чатов")
    except UserAlreadyParticipantError:
        logger.debug("Already patricipant")
        logger.debug("try save")
        await save(telegram_id, url, clear_url, client, db)
        return


async def save(telegram_id, url, clear_url, client, db):
    while True:
        try:
            try:
                chat = await client.get_entity(url)
            except:
                try:
                    chat = await client.get_entity("telegram.me/joinchat/"+url)
                except InviteHashExpiredError:
                    return
            a = db.add_chat(telegram_id, clear_url, chat.id, chat.title)
            logger.debug(f"Succes add chat {clear_url}")
            return
        except IntegrityError:
            logger.debug(f"exist {clear_url}")
            return


async def mailing():
    client_data = "DB CLIENT DATA"
    text = "text"
    phone = client_data[0]
    api_id = client_data[1]
    api_hash = client_data[2]
    telegram_id = ""
    client_chats = "DB CLIENTSCHATS"
    client = TelegramClient(phone, api_id, api_hash)
    message_count = 0
    async with client:
        for chat in client_chats:
            try:
                if message_count > 5:
                    sleep(100)
                    message_count = 0
                await client.send_message(entity=chat, message=text)

            except Exception as ex:
                bot.send_message(
                    telegram_id, f"Возника ошибка при отправке сообщения в чат {chat}, обратитесь к администратору\nОшибка{ex}.\nСпасибо за понимание, со временем ошибок будет все мешьне.")
