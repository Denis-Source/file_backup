class BaseBackupException(Exception):
    pass


class NotFileException(BaseBackupException):
    def __init__(self, record_path):
        self.record_path = record_path

    def __str__(self):
        return f"{self.record_path} is not a file"


class NotFolderException(BaseBackupException):
    def __init__(self, record_path):
        self.record_path = record_path

    def __str__(self):
        return f"{self.record_path} is not a folder"


class NoBasePathSpecifiedException(BaseBackupException):
    def __init__(self, record_path):
        self.record_path = record_path

    def __str__(self):
        return f"No base path for {self.record_path}"
