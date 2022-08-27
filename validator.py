from config import Config
import re


class Validator:
    @staticmethod
    def name_validator(path: str):
        for r in Config.EXCLUDED_NAMES:
            if re.compile(r).match(path):
                return False
        return True

    @staticmethod
    def format_validator(path: str):
        format_ = path.split(".")[-1]
        for f in Config.EXCLUDED_FORMATS:
            if format_ == f:
                return False
        return True
