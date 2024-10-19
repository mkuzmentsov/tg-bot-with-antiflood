from db.connection_manager import *

from db.dao.AbstractDAO import AbstractDAO

class NoOpDao(AbstractDAO):

    def get_user_by_id(self, id: str):
        acc = TgAccount
        acc.id = id
        acc.username = ""
        acc.fullname = ""

    def insert_user(self, id: str, username: str, full_name: str):
        return id

    def insert_message(self, tg_account_id, time, text_content, binary_content):
        return "dummy_id"
