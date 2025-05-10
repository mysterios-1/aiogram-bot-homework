import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv, find_dotenv
from database.engine import create_db
from handlers.user_private import user_private_router
from common.bot_command_list import private
from aiogram.enums import ParseMode
from database.engine import create_db, drop_db, session_maker
from middlewares.db import DataBaseSession

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


load_dotenv(find_dotenv())

ALLOWED_UPDATES = ['message, edited_message']

token = os.getenv("TOKEN")

if token is None:
    print("Ошибка: Не найден токен бота в переменной окружения TOKEN!")
    exit()

bot = Bot(token=token)
bot.my_admins_list = []

dp = Dispatcher()

dp.include_router(user_private_router)

async def on_startup(bot):

    # await drop_db()

    await create_db()

async def on_shutdown(bot):
    print('бот лег')

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    asyncio.run(main())