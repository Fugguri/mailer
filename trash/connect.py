from trash.telethon import TelegramClient
import asyncio


async def conne():
    client = TelegramClient(
        "+79882547866",
        25080938,
        "704a82f7554add37aba76dc949c88b7b",
    )

    await client.connect()
    await client.send_code_request("+79882547866")


asyncio.run(conne())
