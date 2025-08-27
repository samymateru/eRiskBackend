import logging
import sys
from threading import Lock

class LoggerSingleton:
    _instance = None
    _lock = Lock()
    _initialized = False

    def __new__(cls, name="app_logger", level=logging.DEBUG):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name="app_logger", level=logging.DEBUG):
        if self._initialized:
            return

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        self._initialized = True

    def add_console_handler(self, level=logging.DEBUG):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
        return self

    def add_file_handler(self, filepath: str, level=logging.DEBUG):
        file_handler = logging.FileHandler(filepath)
        file_handler.setLevel(level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
        return self

    def set_level(self, level):
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)
        return self

    def set_formatter(self, formatter: logging.Formatter):
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)
        return self

    def get_logger(self) -> logging.Logger:
        return self.logger
