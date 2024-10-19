import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.connection_manager import TgAccount, TgMessage, Base
from db.dao.AbstractDAO import AbstractDAO

class DAO(AbstractDAO):

    def __init__(self):
        self.db_connection_string = os.environ["DB_CONNECTION_STRING"]
        self.engine = create_engine(self.db_connection_string, echo=True)
        self.Session = sessionmaker(bind=self.engine)

        self.init_sqlalchemy()

    def init_sqlalchemy(self):
        if self.db_connection_string:
            Base.metadata.create_all(self.engine)
            print("Created schema")

    def get_user_by_id(self, id: str):
        return self.Session().query(TgAccount).filter_by(id=id).first()

    def insert_user(self, id: str, username: str, full_name: str):
        tg_account = TgAccount(id=id, username=username, fullname=full_name)
        sess = self.Session()
        sess.add(tg_account)
        sess.commit()

        return id

    def insert_message(self, tg_account_id, time, text_content, binary_content):
        tg_message = TgMessage(tg_account_id=tg_account_id, time=time, text_content=text_content,
                               binary_content=binary_content)
        sess = self.Session()
        sess.add(tg_message)
        sess.commit()

        return tg_message.id