from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text, BigInteger, func, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class Homework(Base):
    __tablename__ = 'homeworks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), autoincrement=True)
    deadline: Mapped[DateTime] = mapped_column(DateTime)
    assigned_date: Mapped[DateTime] = mapped_column(DateTime)
    subject: Mapped[str] = mapped_column(nullable=False)

class Schedule(Base):
    __tablename__ = 'schedules'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=False, index=True)
    monday: Mapped[str] = mapped_column(nullable=True)
    tuesday: Mapped[str] = mapped_column(nullable=True)
    wednesday: Mapped[str] = mapped_column( nullable=True)
    thursday: Mapped[str] = mapped_column(nullable=True) 
    friday: Mapped[str] = mapped_column(nullable=True)
    saturday: Mapped[str] = mapped_column(nullable=True)
    sunday: Mapped[str] = mapped_column(nullable=True)

    lessons: Mapped["Lesson"] = relationship(back_populates="schedule", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = 'lessons'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey('schedules.id'), nullable=False)
    subject: Mapped[str] = mapped_column(nullable=False)
    homework: Mapped[str] = mapped_column(default="Нету дз")

    schedule: Mapped["Schedule"] = relationship(back_populates="lessons") 

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)




    # id = Mapped[](Integer, primary_key=True)
    # user_id = Column(Integer, nullable=False)
    # subject = Column(String, nullable=False)
    # task = Column(String, nullable=False)
    # deadline = Column(Date, nullable=False)
    # assigned_date = Column(Date, nullable=False)
    # quarter = Column(Integer)
    # year = Column(Integer)