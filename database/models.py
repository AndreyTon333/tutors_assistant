from sqlalchemy import BigInteger, ForeignKey, String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url="sqlite+aiosqlite:///database/db.sqlite3", echo=False)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Learners(Base):
    __tablename__ = 'learners'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer, default=0)
    username: Mapped[str] = mapped_column(String, default='')
    token: Mapped[str] = mapped_column(String(20))
    fio: Mapped[str] = mapped_column(String, default='')

class Content(Base):
    __tablename__='content'
    id: Mapped[int] = mapped_column(primary_key=True)
    chapter: Mapped[str] = mapped_column(String)
    name_dz: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String, default='')
    content: Mapped[str] = mapped_column(String, default='')
    status: Mapped[int] = mapped_column(Integer, default=1)

class RelationLernersContent(Base):
    __tablename__='relation'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer)
    fio: Mapped[str] = mapped_column(String)
    id_dz: Mapped[str] = mapped_column(String)
    name_dz: Mapped[str] = mapped_column(String)
    deadline: Mapped[str] = mapped_column(String)
    comment_to_execute_dz: Mapped[str] = mapped_column(String, default='')
    executed_dz: Mapped[str] = mapped_column(String, default='')
    comment_executed_dz: Mapped[str] = mapped_column(String, default='')
    checked_dz: Mapped[str] = mapped_column(String, default='')
    comment_checked_dz: Mapped[str] = mapped_column(String, default='')



async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)