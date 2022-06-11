from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


class Config:
    BACKUP_DIRECTORIES = []

    REMOTE_FOLDER = ""

    # Filters
    EXCLUDED_NAMES = [
        r"env$",
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
    LOGGING_COMMAND_LINE_LEVEL = INFO
    LOGGING_FILE_LEVEL = INFO
