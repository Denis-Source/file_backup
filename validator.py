from config import Config
import re


class Validator:
    """
    Various filter functions grouped in a class
    """
    @staticmethod
    def name_validator(path: str):
        """
        Validates path name
        Compares to the names specified in configs

        :param path:    path that should be validated
        :return:        whether the path is validated
        """
        for r in Config.EXCLUDED_NAMES:
            if re.compile(r).match(path):
                return False
        return True

    @staticmethod
    def format_validator(path: str):
        """
        Validates path format
        Compares to the formats specified in configs

        :param path:    path that should be validated
        :return:        whether the path is validated
        """
        format_ = path.split(".")[-1]
        for f in Config.EXCLUDED_FORMATS:
            if format_ == f:
                return False
        return True
