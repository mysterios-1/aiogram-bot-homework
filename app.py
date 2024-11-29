import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.filters import Command

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("Привет! Я бот для помощи с домашними заданиями.\n"
                        "Введите /help, чтобы узнать, как я могу вам помочь.")

@dp.message(Command(commands=['help']))
async def help_command(message: types.Message):
    await message.answer("Я могу:\n"
                        " - Добавлять задачи в расписание: /add_task <день недели> <задачи>\n"
                        " - Удалять задачи из расписания: /remove_task <день недели> <задачи>\n"
                        " - Редактировать задачи в расписании: /edit_task <день недели> <задачи> <новая задачи>\n"
                        " - Добавить расписание: /add_schedule")

async def main():
    await dp.start_polling(bot)

asyncio.run(main())