import asyncio
import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv, find_dotenv
from handlers.user_private import user_private_router
from common.bot_command_list import private
from aiogram.enums import ParseMode

load_dotenv(find_dotenv())

ALLOWED_UPDATES = ['message, edited_message']

bot = Bot(token=os.getenv('TOKEN'))
bot.my_admins_list = []

dp = Dispatcher()

dp.include_router(user_private_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    asyncio.run(main())