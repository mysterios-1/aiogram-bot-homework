from asyncio.log import logger
from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f, StateFilter
from aiogram.utils.formatting import (
    as_list,
    as_marked_section,
    Bold,
)
from database.models import Lesson, Schedule
from kbds.reply import get_keyboard
from sqlalchemy.orm import Session
from sqlalchemy import exc
from database.orm_query import (
    orm_add_schedule,
    orm_add_user,
    orm_get_schedule,
    orm_update_schedule
)
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select


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


class days_of_week(StatesGroup):
    Monday = State()

@user_private_router.message(or_f(Command("add_schedule"), (F.text.lower() == "добавить расписание")))
async def start_add_schedule(message: types.Message, state: FSMContext):
    await message.answer("Введите расписание уроков через запятую (например: Алгебра, Геометрия, Русский язык):")
    await state.set_state(days_of_week.Monday)

@user_private_router.message(days_of_week.Monday, F.text)
async def add_schedule(message: types.Message, state: FSMContext, session):
    schedule_string = message.text
    lessons = [s.strip() for s in schedule_string.split(',')]

    new_schedule = Schedule(user_id=message.from_user.id)
    session.add(new_schedule)
    await session.flush() 

    for i, subject in enumerate(lessons):
        lesson_number = i + 1 
        new_lesson = Lesson(schedule_id=new_schedule.id, lesson_number=lesson_number, subject=subject)
        session.add(new_lesson)

    await session.commit()
    await state.clear()

    await message.answer("Расписание успешно сохранено!")


@user_private_router.message(or_f(Command("show_schedule"), (F.text.lower() == "посмотреть расписание")))
async def show_schedule(message: types.Message, session: AsyncSession):

    user_id = message.from_user.id # здесь lesson.schedule_id равен 8, т.к айди пользователся отличается от айди расписание, а schedule_id равен айди пользователю
    
    # async def get_lessons(session: AsyncSession, schedule_id: int):
    #     stmt = select(Lesson).where(Lesson.schedule_id == schedule_id).order_by(Lesson.lesson_number)
    #     result = await session.execute(stmt)
    #     lessons = result.scalars().all()
    #     return lessons
    # как сделать так чтобы schedule_id в табл Lesson равнялось id в таблице Schedule, учитывая как основу
    # a1 = await get_lessons(session, schedule_id)

    # 1. Получаем schedule_id для user_id (предполагая, что у вас есть session)
    schedule_query = select(Schedule.id).where(Schedule.user_id == user_id)
    result = await session.execute(schedule_query)
    schedule_id = result.scalar_one()

    # 2. Используем schedule_id в запросе к Lesson
    lesson_query = select(Lesson).where(Lesson.schedule_id == schedule_id).order_by(Lesson.lesson_number)
    result = await session.execute(lesson_query)
    lessons = result.scalars().all()

    if not lessons:
        await message.answer("Расписание не найдено. Сначала добавьте расписание.")
        return

    schedule_text = "Ваше расписание:\n"
    for lesson in lessons:
        schedule_text += f"Урок {lesson.lesson_number}: {lesson.subject} {lesson.homework}\n" 

    await message.answer(schedule_text)

