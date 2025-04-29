from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text, BigInteger, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class Homework(Base):
    __tablename__ = 'Homework'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    category_id: Mapped[str] = mapped_column(ForeignKey('categories.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), autoincrement=True)
    deadline: Mapped[DateTime] = mapped_column(DateTime)
    assigned_date: Mapped[DateTime] = mapped_column(DateTime)
    quarter: Mapped[int] = mapped_column(int)


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)


    # id = Mapped[](Integer, primary_key=True)
    # user_id = Column(Integer, nullable=False)
    # subject = Column(String, nullable=False)
    # task = Column(String, nullable=False)
    # deadline = Column(Date, nullable=False)
    # assigned_date = Column(Date, nullable=False)
    # quarter = Column(Integer)
    # year = Column(Integer)