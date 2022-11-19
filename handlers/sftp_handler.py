from typing import List, Union, Callable

from config import Config
from handlers.base_handler import BaseHandler
from logger import Logger
import pysftp

from errors import NoBasePathSpecifiedException, UnableToAccessException, RecordNotFoundException
from records.file import File
from records.folder import Folder


class SFTPHandler(BaseHandler):
    """
    Secure File Transfer Protocol Handler class
    Inherits from BaseHandler

    Constants:
        HANDLER_NAME    name of the handler
        LOGGER          logger instance
        CONNECTION      sftp connection based on pysftp.Connection
    """

    HANDLER_NAME = "sftp"
    LOGGER = Logger(HANDLER_NAME)
    CONNECTION = None

    def __init__(self, validators: List[Callable] = None):
        super().__init__(validators)
        if not self.CONNECTION:
            self.CONNECTION = pysftp.Connection(
                username=Config.SFTP_USERNAME,
                host=Config.SFTP_HOST,
                private_key=Config.SFTP_KEY_LOCATION
            )

    def get_file_stat(self, path: str) -> dict:
        """
        Returns the following stats about the specified file
        in a form of a dictionary:
            modified
            size
        pysftp cannot provide id of the file
        Uses pysftp.Connection stat() method to access file information

        :param path: location of the file
        :return: dictionary with the specified information
        """

        self.LOGGER.debug(f"Getting information about a file at {path}")
        if not self.CONNECTION.isfile(path):
            self.LOGGER.warning(f"{path} is not a file")

        stat = self.CONNECTION.stat(path)
        self.LOGGER.info(f"Got information about a file at {path}")

        return {
            "modified": stat.st_mtime,
            "size": stat.st_size,
        }

    def get_folder_stat(self, path: str) -> dict:
        """
        Returns the following stats about the specified folder
        in a form of a dictionary:
            created
            size
        pysftp cannot provide id of the file
        Uses pysftp.Connection stat() method to access file information


        :param path: location of the folder
        :return: dictionary with the specified information
        """

        self.LOGGER.debug(f"Getting information about a folder at {path}")
        if not self.CONNECTION.isdir(path):
            self.LOGGER.warning(f"{path} is not a file")
        stat = self.CONNECTION.stat(path)
        self.LOGGER.info(f"Got information about a folder at {path}")
        return {
            "modified": stat.st_mtime,
            "size": stat.st_size
        }

    def get_file_content(self, file: File) -> bytes:
        """
        Returns file content in bytes
        Uses pysftp open() to get file contents

        :raises UnableToAccessException: if a file could not be read

        :param file: File object instance
        :return: file contents in bytes
        """

        self.LOGGER.debug(f"Getting file content at {file.path}")
        try:
            with self.CONNECTION.open(file.path, "rb") as f:
                self.LOGGER.info(f"File at {file.path} is read")
                return f.read()
        except (OSError, FileNotFoundError, PermissionError):
            self.LOGGER.error(f"Cant read file {file.path}")
            raise UnableToAccessException(file.path)

    def upload_structure(self, folder: Folder, content: bytes) -> File:
        """
        Saves folder the structure JSON in a specified folder

        :raises UnableToAccessException: if the file could not be accessed

        :param folder:  Folder object instance to upload file into
        :param content: bytes to load in the file
        :return:        newly created File object instance
        """

        self.LOGGER.info(f"Updating file structure in {folder.path} content")
        file_path = f"{folder.path}/structure.json"

        try:
            with self.CONNECTION.open(file_path, "wb") as f:
                f.write(content)
        except (OSError, PermissionError):
            self.LOGGER.error(f"Unable to create {file_path}")
            raise UnableToAccessException(file_path)

        return File(
            file_path,
            self
        )

    def upload_file(self, file: File, remote_folder: Folder) -> File:
        """
        Copies the specified file into a remote folder

        :raises UnableToAccessException: if a file cannot be uploaded

        :param file:            File object instance
        :param remote_folder:   Folder object instance

        :return: new File instance
        """

        self.LOGGER.debug(f"Uploading file from {file.path} to {remote_folder.path}")

        new_file_path = f"{remote_folder.path}/{file.name}"
        try:
            with self.CONNECTION.open(new_file_path, "wb") as f:
                size = f.write(file.get_content())
            self.CONNECTION.sftp_client.utime(new_file_path, (file.modified, file.modified))
        except (PermissionError, OSError):
            self.LOGGER.warning(f"Cant create a file {new_file_path}")
            raise UnableToAccessException(new_file_path)

        uploaded_file = File(
            path=new_file_path,
            handler=self,
            stat={
                "size": size,
                "modified": file.modified
            }
        )

        self.LOGGER.info(f"Created new file at {new_file_path}")
        return uploaded_file

    def upload_folder(self, folder: Folder, new_folder_path: str, with_content=False) -> Folder:
        """
        Copies the specified Folder object instance into a remote path
        Copies the contents of the folder if needed

        Uses os.makedirs() to create folders
        Uses upload_file() to upload file as contents of a folder
        thus preserves file metadata

        :raises NoBasePathSpecifiedException: if the folder base path is not specified
        :raises UnableToAccessException: if the folder cannot be accessed

        :param folder: Folder object instance to copy from
        :param new_folder_path: string path to copy to
        :param with_content: whether to copy folder contents
        :return: newly created Folder object instance
        """

        self.LOGGER.debug(f"Uploading file from {folder.path} to {new_folder_path}")

        if folder.base_location:
            folder_relative_path = folder.path.replace(folder.base_location, "")
        else:
            self.LOGGER.warning(f"Cant upload folder at {folder.path}, no base path specified")
            raise NoBasePathSpecifiedException(folder.path)

        new_base_folder_path = new_folder_path
        new_folder_path = f"{new_folder_path}{folder_relative_path}"
        try:
            self.LOGGER.info(f"Creating folder at {new_folder_path}")
            self.CONNECTION.makedirs(new_folder_path)
            self.CONNECTION.sftp_client.utime(new_folder_path, (folder.modified, folder.modified))
        except FileExistsError:
            self.LOGGER.info(f"Folder at {new_folder_path} is already exists")
        except OSError:
            self.LOGGER.warning(f"Cant create folder at {new_folder_path}")
            raise UnableToAccessException(new_folder_path)

        new_folder = Folder(new_folder_path, self)

        if with_content:
            self.LOGGER.debug(f"Сopying the contents of the folder at {folder.path} to {new_folder_path}")

            for path, record in folder.children.items():
                if self.validate(path):
                    self.LOGGER.info(f"Сopying {record.__class__.__name__} at {record.path}")
                    try:
                        if isinstance(record, File):
                            file = self.upload_file(record, new_folder)
                            new_folder.add_child(file)
                        else:
                            folder = self.upload_folder(record, new_base_folder_path, with_content=True)
                            new_folder.add_child(folder)
                    except UnableToAccessException:
                        self.LOGGER.warning(f"Cant create a child record in folder {folder.path}")
                else:
                    self.LOGGER.info(f"{path} is not validated, skipping")

        return new_folder

    def get_folder_content(self, folder: Folder) -> List[Union[File, Folder]]:
        """
        Gets the folder content in a form of files and folders
        :param folder: Folder object instance
        :return: List of File and Folder objects

        Uses pysftp module
        """

        self.LOGGER.debug(f"Getting folder content at {folder.path}")
        records = []
        for record_path in self.CONNECTION.listdir(folder.path):
            if self.validate(record_path):
                try:
                    record_path = f"{folder.path}/{record_path}"
                    if self.CONNECTION.isfile(record_path):
                        records.append(File(
                            record_path, self
                        ))
                    else:
                        records.append(Folder(
                            record_path,
                            self,
                            folder.base_location
                        ))
                except (UnableToAccessException, RecordNotFoundException):
                    self.LOGGER.warning(f"Error handling record at {record_path}")
            else:
                self.LOGGER.info(f"{record_path} is not validated, skipping")
        return records
