from abc import ABC, abstractmethod


class AbstractDAO(ABC):
    @abstractmethod
    def get_user_by_id(self, id: str):
        pass

    @abstractmethod
    def insert_user(self, id: str, username: str, full_name: str):
        pass

    @abstractmethod
    def insert_message(self, tg_account_id, time, text_content, binary_content):
        pass
