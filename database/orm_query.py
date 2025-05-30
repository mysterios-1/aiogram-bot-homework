import math
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models import Lesson, User, Schedule

async def orm_add_user(
    session: AsyncSession,
    user_id: int,

):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(user_id=user_id)
        )
        await session.commit()
        
async def orm_check_user(session: AsyncSession, user_id: int) -> bool:
    try:
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalars().first()
        return user is not None
    except Exception as e:
        print(f"Ошибка при проверке пользователя: {e}")
        return False

async def orm_add_schedule(session:AsyncSession, data:dict):
    obj = Schedule(
        monday = data['monday'],
        tuesday = data['tuesday'],
        wednesday = data['wednesday'],
        thursday = data['thursday'],
        friday = data['friday'],
        saturday = data['saturday'],
        user_id = data['user_id']
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj) 
    return obj

async def orm_add_lessons_unique_by_schedule(session: AsyncSession, lessons: set, schedule_id: int):

    result = await session.execute(
        select(Lesson.subject).where(Lesson.schedule_id == schedule_id, Lesson.subject.in_(lessons))
    )
    existing_lessons = set(row[0] for row in result.all())

    new_lessons = lessons - existing_lessons

    for lesson_name in new_lessons:
        lesson_obj = Lesson(subject=lesson_name, schedule_id=schedule_id)
        session.add(lesson_obj)

    await session.commit()

async def get_lessons(session: AsyncSession, schedule_id: int):
    """Получает уроки для определенного расписания."""
    stmt = select(Lesson).where(Lesson.schedule_id == schedule_id).order_by(Lesson.lesson_number)
    result = await session.execute(stmt)
    lessons = result.scalars().all()
    return lessons

async def get_schedule_data(session: AsyncSession, schedule_id: int):
    """Получает данные расписания по ID."""
    stmt = select(Schedule).where(Schedule.id == schedule_id)
    result = await session.execute(stmt)
    schedule = result.scalar_one_or_none()
    return schedule


async def orm_update_schedule(session: AsyncSession, schedule_id: int, data):
    query = (
        update(Schedule)
        .where(Schedule.id == schedule_id)
        .values(
            monday = data['monday'],
            tuesday = data['tuesday'],
            wednesday = data['wednesday'],
            thursday = data['thursday'],
            friday = data['friday'],
            saturday = data['saturday']
        )
    )
    await session.execute(query)
    await session.commit()


async def orm_get_schedule(session: AsyncSession, schedule_id: int):
    query = select(Schedule).where(Schedule.id == schedule_id)
    result = await session.execute(query)
    return result.scalar()





# async def orm_add_product(session: AsyncSession, data: dict):
#     obj = Product(
#         name=data["name"],
#         description=data["description"],
#         price=float(data["price"]),
#         image=data["image"],
#         category_id=int(data["category"]),
#     )
#     session.add(obj)
#     await session.commit()