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
    get_lessons,
    get_schedule_data,
    orm_add_lessons_unique_by_schedule,
    orm_add_schedule,
    orm_add_user,
    orm_check_user,
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

class AddSchedule(StatesGroup):
    monday = State()
    tuesday = State()
    wednesday = State()
    thursday = State()
    friday = State()
    saturday = State()
    sunday = State()  # Добавим состояние для воскресенья

    schedule_for_change = None

    texts = {
        "AddSchedule:monday": "Введите расписание на понедельник:",
        "AddSchedule:tuesday": "Введите расписание на вторник:",
        "AddSchedule:wednesday": "Введите расписание на среду:",
        "AddSchedule:thursday": "Введите расписание на четверг:",
        "AddSchedule:friday": "Введите расписание на пятницу:",
        "AddSchedule:saturday": "Введите расписание на субботу:",
        "AddSchedule:sunday": "Введите расписание на воскресенье:",
    }


@user_private_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_schedule_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    schedule_id = callback.data.split("_")[-1]

    schedule_for_change = await orm_get_schedule(session, int(schedule_id))

    AddSchedule.schedule_for_change = schedule_for_change

    await callback.answer()
    await callback.message.answer(
        "Введите расписание на понедельник:", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddSchedule.monday)


@user_private_router.message(or_f(Command("add_schedule"), (F.text.lower() == "добавить  расписание")))
async def add_schedule(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите расписание на понедельник:", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddSchedule.monday)


@user_private_router.message(StateFilter("*"), Command("отмена"))
@user_private_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddSchedule.schedule_for_change:
        AddSchedule.schedule_for_change = None
    await state.clear()
    await message.answer("Действия отменены", reply_markup=types.ReplyKeyboardRemove())


@user_private_router.message(StateFilter("*"), Command("назад"))
@user_private_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddSchedule.monday:
        await message.answer(
            "Предыдущего шага нет, или введите название товара или напишите 'отмена'"
        )
        return

    previous = None
    for step in AddSchedule.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddSchedule.texts[previous.state]}"
            )
            return
        previous = step

@user_private_router.message(AddSchedule.monday, F.text)
async def add_monday(message: types.Message, state: FSMContext):
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(monday=AddSchedule.schedule_for_change.monday)
    else:
        # Здесь можно сделать какую либо дополнительную проверку
        # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
        # например:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "Длина расписания не должна превышать 150 символов\nили быть менее 5ти символов. \n Введите заново"
            )

            return

        await state.update_data(monday=message.text)
    await message.answer("Введите расписание на вторник:")
    await state.set_state(AddSchedule.tuesday)


@user_private_router.message(AddSchedule.monday)
async def add_monday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, понедельник")


@user_private_router.message(AddSchedule.tuesday, F.text)
async def add_tuesday(message: types.Message, state: FSMContext):
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(tuesday=AddSchedule.schedule_for_change.tuesday)
    else:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "Длина расписания не должна превышать 150 символов\nили быть менее 5ти символов. \n Введите заново"
            )

            return

        await state.update_data(tuesday=message.text)
    await message.answer("Введите расписание на среду:")
    await state.set_state(AddSchedule.wednesday)


@user_private_router.message(AddSchedule.tuesday)
async def add_tuesday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, вторник")


@user_private_router.message(AddSchedule.wednesday, F.text)
async def add_wednesday(message: types.Message, state: FSMContext):
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(wednesday=AddSchedule.schedule_for_change.wednesday)
    else:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "Длина расписания не должна превышать 150 символов\nили быть менее 5ти символов. \n Введите заново"
            )

            return

        await state.update_data(wednesday=message.text)
    await message.answer("Введите расписание на четверг:")
    await state.set_state(AddSchedule.thursday)


@user_private_router.message(AddSchedule.wednesday)
async def add_wednesday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, среда")


@user_private_router.message(AddSchedule.thursday, F.text)
async def add_thursday(message: types.Message, state: FSMContext):
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(thursday=AddSchedule.schedule_for_change.thursday)
    else:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "Длина расписания не должна превышать 150 символов\nили быть менее 5ти символов. \n Введите заново"
            )

            return

        await state.update_data(thursday=message.text)
    await message.answer("Введите расписание на пятницу:")
    await state.set_state(AddSchedule.friday)


@user_private_router.message(AddSchedule.thursday)
async def add_thursday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, четверг")


@user_private_router.message(AddSchedule.friday, F.text)
async def add_friday(message: types.Message, state: FSMContext):
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(friday=AddSchedule.schedule_for_change.friday)
    else:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "Длина расписания не должна превышать 150 символов\nили быть менее 5ти символов. \n Введите заново"
            )

            return

        await state.update_data(friday=message.text)
    await message.answer("Введите расписание на субботу:")
    await state.set_state(AddSchedule.saturday)


@user_private_router.message(AddSchedule.friday)
async def add_friday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, пятница")


@user_private_router.message(AddSchedule.saturday, F.text)
async def add_saturday(message: types.Message, state: FSMContext):
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(saturday=AddSchedule.schedule_for_change.saturday)
    else:
        await state.update_data(saturday=message.text)
    await message.answer("Введите расписание на воскресенье:")  # Добавляем вопрос про воскресенье
    await state.set_state(AddSchedule.sunday)


@user_private_router.message(AddSchedule.saturday)
async def add_saturday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, суббота")


@user_private_router.message(AddSchedule.sunday, F.text)
async def add_sunday(message: types.Message, state: FSMContext, session: AsyncSession):
    logger.debug("add_sunday хэндлер вызван")
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(sunday=AddSchedule.schedule_for_change.sunday)
    else:
        await state.update_data(sunday=message.text)

    data = await state.get_data()

    try:
        user = message.from_user
        user_exists = await orm_check_user(session, user.id)
        if not user_exists:
            await orm_add_user(
                session,
                user_id=user.id,
            )

        if AddSchedule.schedule_for_change:
            await orm_update_schedule(session, AddSchedule.schedule_for_change.id, data)
        else:
            data['user_id'] = message.from_user.id
            new_schedule = await orm_add_schedule(session, data)
            schedule_id = new_schedule.id
        
        all_lessons = []
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for day in days_of_week:
            if day in data and data[day]:
                lessons = [l.strip() for l in data[day].split(',')]
                all_lessons.extend(lessons)

        unique_lessons = set(all_lessons)

        await orm_add_lessons_unique_by_schedule(session, unique_lessons, schedule_id) #Тут должен быть schedule_id который есть

        await message.answer("Расписание добавлено/изменено", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()

    except Exception as e:
        await message.answer(
            f"Ошибка: \n{str(e)}\nОбратитесь к программисту.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.clear()
        AddSchedule.schedule_for_change = None


@user_private_router.message(AddSchedule.sunday)  # Обработчик некорректного ввода для воскресенья
async def add_sunday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, воскресенье")

@user_private_router.message(or_f(Command("show_schedule"), (F.text.lower() == "посмотреть расписание")))
async def show_schedule(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id

    # Получаем schedule_id для user_id
    schedule_query = select(Schedule.id).where(Schedule.user_id == user_id)
    result = await session.execute(schedule_query)
    schedule_id = result.scalar_one_or_none()  # Используем scalar_one_or_none для обработки случаев, когда расписание не найдено

    if schedule_id is None:
        await message.answer("Расписание не найдено schedule id. Сначала добавьте расписание.")
        return

    schedule_text = "Ваше расписание:\n"

    # Разделяем уроки по дням недели
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    schedule_data = await get_schedule_data(session, schedule_id)

    for day in days:
        lessons_for_day = getattr(schedule_data, day.lower())
        schedule_text += f"\n{day}:\n"
        if lessons_for_day:
            schedule_text += f"{lessons_for_day}\n"
        else:
            schedule_text += "  Нет уроков\n"
    await message.answer(schedule_text)



