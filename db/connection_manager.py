

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TgAccount(Base):
    __tablename__ = "tg_accounts"

    id = Column(String, primary_key=True)
    username = Column(String)
    fullname = Column(String)


class TgMessage(Base):
    __tablename__ = "tg_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_account_id = Column(String, ForeignKey("tg_accounts.id"))
    time = Column(DateTime)
    text_content = Column(String)
    binary_content = Column(String)