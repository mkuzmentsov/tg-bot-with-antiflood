import os
import logging

logger = logging.getLogger(__name__)

filename = "userdb"


class UserDBManager(object):
    _dict = {}

    def __init__(self):
        self._init_file()

    def _init_file(self):
        if not os.path.exists(filename):
            with open(filename, "w"):
                print(f"{filename} file created")
        self._init_user_list()

    def _read_file_contents(self):
        with open(filename, "r") as f:
            return f.read()

    def _init_user_list(self):
        content = self._read_file_contents()
        userdata_list = content.split("\n")
        while "" in userdata_list:
            userdata_list.remove("")
        for userdata in userdata_list:
            userdata_array = userdata.split(",")
            self._dict[userdata_array[0]] = userdata_array
            logger.info(f"id={userdata[0]}, data={userdata}")

    def get_data(self, userid: str):
        return self._dict.get(userid, [])


