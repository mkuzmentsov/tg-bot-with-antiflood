import psycopg2
import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker

db_connection_string = os.environ["DB_CONNECTION_STRING"]
engine = create_engine(db_connection_string, echo=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)

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


def init_sqlalchemy():
    Base.metadata.create_all(engine)
    print("Created schema")