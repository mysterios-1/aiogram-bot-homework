from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import (
    as_list,
    as_marked_section,
    Bold,
)
from kbds.reply import get_keyboard

user_private_router = Router()

@user_private_router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "Привет, я бот который помогает записывать д/з",
                         reply_markup=get_keyboard(
                             "О боте",
                             "Добавить расписание",
                             "Изменить расписание",
                             "Добавить д/з",
                             "Изменить д/з",
                             placeholder="Что интересует?",
                             sizes=(2,2,2)
                         ),
                        )
    
@user_private_router.message(or_f(Command("menu"), (F.text.lower() == "меню")))
async def menu_cmd(message: types.Message):
    await message.answer("Вот меню:")

@user_private_router.message(or_f(Command("about"), (F.text.lower() == "о боте")))
async def about_cmd(message: types.Message):
    await message.answer("О нас:")


# @dp.message_handler(state='waiting_for_schedule')
# async def process_schedule(message: types.Message, state: FSMContext):
#     schedule_str = message.text
#     lessons = [lesson.strip() for lesson in schedule_str.split(',')]

#     if len(lessons) != 7:
#         await message.reply("Должно быть 7 уроков!")
#         return

#     # ... (здесь нужно добавить обработку дня недели от пользователя) ...
#     # ... (добавление в базу данных с помощью вашей функции add_schedule) ...