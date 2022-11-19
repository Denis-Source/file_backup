from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


class Config:
    # SFTP
    SFTP_HOST = ""
    SFTP_USERNAME = "root"
    SFTP_KEY_LOCATION = ""

    # GDRIVE
    GDRIVE_CREDENTIALS_FILE = "client_secrets.json"
    GDRIVE_TOKEN_FILE = "token.json"

    # DROPBOX
    DROPBOX_TOKEN = ""

    # Filters
    EXCLUDED_NAMES = [
        r"^__",
        r"l_env",
        r"env",
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
