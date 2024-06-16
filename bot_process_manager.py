import os
import time
from threading import Thread
from enum import Enum
import hashlib
import logging

class State(Enum):
    RUNNING = "True"


process_filename = "process"

logger = logging.getLogger(__name__)

class BotProcessManager(object):
    running: bool = False

    def on_state_changed(self, r: bool) -> None:
        None

    def __init__(self):
        self._init_file()
        self._init_observer()

    def _on_file_modified(self):
        self._refresh_app_state()
        self.on_state_changed(self.running)

    def _observer_function(self):
        last_modified_time = os.path.getmtime(process_filename)
        while True:
            modify_time = os.path.getmtime(process_filename)
            if modify_time > last_modified_time:
                self._on_file_modified()
                last_modified_time = modify_time

            time.sleep(2)

    def _init_observer(self):
        observer = Thread(target=self._observer_function)
        observer.start()
        logger.info("Started bot process manager observer")

    def _init_file(self):
        if not os.path.exists(process_filename):
            with open(process_filename, "w") as file:
                file.write(State.RUNNING.value)
        self._refresh_app_state()

    def _read_file_contents(self):
        with open(process_filename, "r") as f:
            return f.read()

    def _refresh_app_state(self):
        with open(process_filename, "r") as f:
            state = f.read()
            self.running = state == State.RUNNING.value
            print(f"App state is_running={self.running}")



