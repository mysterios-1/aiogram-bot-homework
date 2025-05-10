from asyncio.log import logger
from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f, StateFilter
from aiogram.utils.formatting import (
    as_list,
    as_marked_section,
    Bold,
)
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


# @user_private_router.message(or_f(Command('add_sсhedule')))
# async def add_schedule_async(message, user_private):
#     days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
#     current_day = days[0]

#     async def process_day_async(message, current_day, user_private):
#         # await message.answer('Введите расписание, начиная с понедельника. Вводится через запятую, пример: Алгебра, Русский язык, Информатика')
#         schedule_input = message.text.strip()
#         if not schedule_input:
#             await message.answer("Расписание не может быть пустым.")
#             return
        
#             subjects = [s.strip() for s in schedule_input.split(',')]
#             async with Session() as session: # Асинхронный контекстный менеджер
#                 for subject_name in subjects:
#                     new_schedule_entry = Schedule(user_id=user_private, day_of_week=current_day, subject=subject_name)
#                     session.add(new_schedule_entry)
#                     try:
#                         await session.commit() # await для асинхронного commit
#                     except exc.IntegrityError as e:
#                         await session.rollback()
#                         await message.answer("Ошибка добавления: {e}")

#             next_day_index = days.index(current_day) + 1
#             if next_day_index < len(days):
#                 next_day = days[next_day_index]
#                 msg = await message.answer(f"Введите расписание на {next_day}:") # await для reply_to
#                 dp.register_message_handler(process_day_async, lambda message: message.from_user.id == user_private, content_types=types.ContentType.TEXT)
#             else:
#                 await message.answer("Расписание сохранено!") # await для reply_to
#         except Exception as e:
#             await message.answer(f"Произошла ошибка: {e}") # await для reply_to
            
#     if user_private: # проверка на None
#         msg = await message.answer(f"Введите расписание на {current_day}:")
#         dp.register_message_handler(process_day_async, lambda message: message.from_user.id == user_private, content_types=types.ContentType.TEXT)




# @dp.message_handler(state='waiting_for_schedule')
# async def process_schedule(message: types.Message, state: FSMContext):
#     schedule_str = message.text
#     lessons = [lesson.strip() for lesson in schedule_str.split(',')]

#     if len(lessons) != 7:
#         await message.reply("Должно быть 7 уроков!")
#         return

#     # ... (здесь нужно добавить обработку дня недели от пользователя) ...
#     # ... (добавление в базу данных с помощью вашей функции add_schedule) ...


class AddSchedule(StatesGroup):
    monday = State()
    tuesday = State()
    wednesday = State()
    thursday = State()
    friday = State()
    saturday = State()

    schedule_for_change = None


    texts = {
        "AddSchedule:monday": "Введите расписание на понедельник заново:",
        "AddSchedule:tuesday": "Введите расписание на вторник заново:",
        "AddSchedule:wednesday": "Введите расписание на среду заново:",
        "AddSchedule:thursday": "Введите расписание на четверг заново:",
        "AddSchedule:friday": "Введите расписание на пятницу заново:",
        "AddSchedule:saturday": "Введите расписание на суботту заново:",
    }

@user_private_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_product_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split("_")[-1]

    schedule_for_change = await orm_get_schedule(session, int(product_id))

    AddSchedule.schedule_for_change = schedule_for_change

    await callback.answer()
    await callback.message.answer(
        "Введите расписание на понедельник:", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddSchedule.monday)

@user_private_router.message(StateFilter(None), F.text == "Добавить расписание")
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

# Вернутся на шаг назад (на прошлое состояние)
@user_private_router.message(StateFilter("*"), Command("назад"))
@user_private_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddSchedule.monday:
        await message.answer(
            'Предыдущего шага нет, или введите название товара или напишите "отмена"'
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
                "Название товара не должно превышать 150 символов\nили быть менее 5ти символов. \n Введите заново"
            )
            
            return

        await state.update_data(monday=message.text)
    await message.answer("Введите расписание на вторник:")
    await state.set_state(AddSchedule.tuesday)

# Хендлер для отлова некорректных вводов для состояния monday
@user_private_router.message(AddSchedule.monday)
async def add_monday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, понедельник")

@user_private_router.message(AddSchedule.tuesday, F.text)
async def add_tuesday(message: types.Message, state: FSMContext):
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(tuesday=AddSchedule.schedule_for_change.tuesday)
    else:
        # Здесь можно сделать какую либо дополнительную проверку
        # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
        # например:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "Название товара не должно превышать 150 символов\nили быть менее 5ти символов. \n Введите заново"
            )
            
            return

        await state.update_data(tuesday=message.text)
    await message.answer("Введите расписание на среду:")
    await state.set_state(AddSchedule.wednesday)

# Хендлер для отлова некорректных вводов для состояния monday
@user_private_router.message(AddSchedule.tuesday)
async def add_tuesday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, вторник")

@user_private_router.message(AddSchedule.wednesday, F.text)
async def add_wednesday(message: types.Message, state: FSMContext):
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(wednesday=AddSchedule.schedule_for_change.wednesday)
    else:
        # Здесь можно сделать какую либо дополнительную проверку
        # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
        # например:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "Название товара не должно превышать 150 символов\nили быть менее 5ти символов. \n Введите заново"
            )
            
            return

        await state.update_data(wednesday=message.text)
    await message.answer("Введите расписание на четверг:")
    await state.set_state(AddSchedule.thursday)

# Хендлер для отлова некорректных вводов для состояния monday
@user_private_router.message(AddSchedule.wednesday)
async def add_wednesday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, среда")

@user_private_router.message(AddSchedule.thursday, F.text)
async def add_thursday(message: types.Message, state: FSMContext):
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(thursday=AddSchedule.schedule_for_change.thursday)
    else:
        # Здесь можно сделать какую либо дополнительную проверку
        # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
        # например:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "Название товара не должно превышать 150 символов\nили быть менее 5ти символов. \n Введите заново"
            )
            
            return

        await state.update_data(thursday=message.text)
    await message.answer("Введите расписание на пятницу:")
    await state.set_state(AddSchedule.friday)

# Хендлер для отлова некорректных вводов для состояния monday
@user_private_router.message(AddSchedule.thursday)
async def add_thursday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, четверг")

@user_private_router.message(AddSchedule.friday, F.text)
async def add_friday(message: types.Message, state: FSMContext):
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(friday=AddSchedule.schedule_for_change.friday)
    else:
        # Здесь можно сделать какую либо дополнительную проверку
        # и выйти из хендлера не меняя состояние с отправкой соответствующего сообщения
        # например:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "Название товара не должно превышать 150 символов\nили быть менее 5ти символов. \n Введите заново"
            )
            
            return

        await state.update_data(friday=message.text)
    await message.answer("Введите расписание на суботту:")
    await state.set_state(AddSchedule.saturday)

# Хендлер для отлова некорректных вводов для состояния monday
@user_private_router.message(AddSchedule.friday)
async def add_friday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, пятница")

@user_private_router.message(AddSchedule.saturday, F.text)
async def add_saturday(message: types.Message, state: FSMContext, session: AsyncSession):
    logger.debug("add_saturday хэндлер вызван")
    if message.text == "." and AddSchedule.schedule_for_change:
        await state.update_data(saturday=AddSchedule.schedule_for_change.saturday)
    else:
        await state.update_data(saturday=message.text)
        data = await state.get_data()
    try:
        if AddSchedule.schedule_for_change:
            await orm_update_schedule(session, AddSchedule.schedule_for_change.id, data)
        else:
            await orm_add_schedule(session, data)
        await message.answer("Расписание добавлено/изменено", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()

    except Exception as e:
        await message.answer(
            f"Ошибка: \n{str(e)}\nОбратись к программеру, он опять денег хочет",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await state.clear()

        AddSchedule.schedule_for_change = None

# Хендлер для отлова некорректных вводов для состояния monday
@user_private_router.message(AddSchedule.saturday)
async def add_saturday2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, суббота")
