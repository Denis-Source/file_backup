import logging

from config import Config


class Logger(logging.Logger):
    """
    Logger class
    Specifies handlers and format
    """
    LOGGER_FORMAT = "%(asctime)s\t%(levelname)-7s\t%(name)-12s\t%(message)s"

    def __init__(self, name):
        super().__init__(name)
        self.add_c_handler()
        self.add_f_handler()

    def add_c_handler(self) -> None:
        """
        Adds stdout handler

        :return: None
        """
        handler = logging.StreamHandler()
        handler.setLevel(Config.LOGGING_COMMAND_LINE_LEVEL)
        formatter = logging.Formatter(self.LOGGER_FORMAT)
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def add_f_handler(self) -> None:
        """
        Adds file handler

        :return: None
        """
        handler = logging.FileHandler(Config.LOGGING_FILE)
        handler.setLevel(Config.LOGGING_FILE_LEVEL)
        formatter = logging.Formatter(self.LOGGER_FORMAT)
        handler.setFormatter(formatter)
        self.addHandler(handler)
