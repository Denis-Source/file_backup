from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


class Config:
    HOST = "8.8.8.8"
    USERNAME = "root"
    KEY_LOCATION = "location_key"

    BACKUP_DIRECTORIES = []

    REMOTE_FOLDER = ""

    # Filters
    EXCLUDED_NAMES = [
        r"^__",
        r"^env",
        r"^venv",
        r"^\.",
        "^node_modules$",
        "^lib$",
        "^dist$",
        "^build$"
    ]

    EXCLUDED_FORMATS = [
        "pyc",
        "pyd",
        "lnk",
        "toc"
    ]

    # Logging
    LOGGING_FILE = "file_backup.log"
    LOGGING_COMMAND_LINE_LEVEL = DEBUG
    LOGGING_FILE_LEVEL = WARNING
