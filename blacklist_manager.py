import os
import re
import logging

logger = logging.getLogger(__name__)

filename = "blacklist"


class BlacklistManager(object):
    def __init__(self):
        self._init_file()

    def _init_file(self):
        if not os.path.exists(filename):
            with open(filename, "w"):
                print("blacklist file created")

    def _read_file_contents(self):
        with open(filename, "r") as f:
            return f.read()

    def is_blacklisted(self, userid):
        userid = str(userid)
        content = self._read_file_contents()
        ids_list = re.split("[\n,;]", content)
        ids_set = set(ids_list)
        logger.info(f"ids_set={ids_set}, userid={userid}")

        return userid in ids_set



