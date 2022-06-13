class BaseBackupException(Exception):
    pass


class RecordNotFoundException(BaseBackupException):
    def __init__(self, record_path):
        self.record_path = record_path

    def __str__(self):
        return f"{self.record_path} not found"


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


class UnableToAccessException(BaseBackupException):
    def __init__(self, record_path):
        self.record_path = record_path

    def __str__(self):
        return f"unable to read record {self.record_path}"


class NoBasePathSpecifiedException(BaseBackupException):
    def __init__(self, record_path):
        self.record_path = record_path

    def __str__(self):
        return f"No base path for {self.record_path}"


class NoConnectionException(BaseBackupException):
    def __init__(self, connection_name):
        self.connection_name = connection_name

    def __str__(self):
        return f"Cant connect to {self.connection_name}"
