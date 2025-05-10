import math
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models import User, Schedule

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

async def orm_add_schedule(session:AsyncSession, data:dict):
    obj = Schedule(
        monday = data['monday'],
        tuesday = data['tuesday'],
        wednesday = data['wednesday'],
        thursday = data['thursday'],
        friday = data['friday'],
        saturday = data['saturday']
    )
    session.add(obj)
    await session.commit()

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