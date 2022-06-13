import json
import os

from typing import List, Union

from handlers.base_handler import BaseHandler
from errors import NoBasePathSpecifiedException, RecordNotFoundException, NotFileException, NotFolderException, \
    UnableToAccessException
from records.folder import Folder
from records.file import File

from logger import Logger


class LocalHandler(BaseHandler):
    """
    Local Handler class
    Uses local filesystem to access the files
    Inherits from BaseHandler

    Constants:
        HANDLER_NAME    name of the handler
        LOGGER          logger instance
    """
    HANDLER_NAME = "local handler"
    LOGGER = Logger(HANDLER_NAME)

    def get_file_stat(self, path: str) -> dict:
        """
        Returns the following stats about the specified file
        in a form of a dictionary:
            modified
            size
            id
        Uses os.stat to access a file

        :raises RecordNotFoundException: if record is not found
        :raises NotFileException:        if record is not a file

        :param path: location of the file
        :return: dictionary with the specified information
        """
        self.LOGGER.debug(f"Getting information about a file at {path}")

        if not os.path.exists(path):
            self.LOGGER.warning(f"File {path} not found")
            raise RecordNotFoundException(path)

        if not os.path.isfile(path):
            self.LOGGER.warning(f"{path} is not a file")
            raise NotFileException(path)

        stat = os.stat(path)
        self.LOGGER.info(f"Got information about a file at {path}")

        return {
            "modified": stat.st_mtime,
            "size": stat.st_size,
            "id": stat.st_ino
        }

    def get_folder_stat(self, path: str) -> dict:
        """
        Returns the following stats about the specified folder
        in a form of a dictionary:
            modified
            size
            id
        Uses os.stat to access a folder

        :raises RecordNotFoundException: if record is not found
        :raises NotFolderException:      if record is not a file

        :param path:    location of the folder
        :return:        dictionary with the specified information
        """
        self.LOGGER.debug(f"Getting information about a folder at {path}")

        if not os.path.exists(path):
            self.LOGGER.info(f"Folder {path} not found")
            raise RecordNotFoundException(path)

        if not os.path.isdir(path):
            self.LOGGER.warning(f"{path} is not a folder")
            raise NotFolderException(path)

        stat = os.stat(path)
        self.LOGGER.info(f"Got information about a folder at {path}")

        return {
            "modified": stat.st_mtime,
            "size": stat.st_size,
            "id": stat.st_ino
        }

    def get_file_content(self, file: File) -> bytes:
        """
        Returns file content in bytes
        Uses default open() to get file content

        :raises UnableToAccessException: if file a could not be read

        :param file: File object instance
        :return: file contents in bytes
        """
        self.LOGGER.debug(f"Getting file content at {file.path}")

        try:
            with open(file.path, "rb") as f:
                self.LOGGER.info(f"File at {file.path} is read")
                return f.read()
        except (FileNotFoundError, PermissionError):
            self.LOGGER.error(f"Cant read file {file.path}")
            raise UnableToAccessException(file.path)

    def set_file_content(self, file: File, content: bytes) -> None:
        """
        Updates file content
        The file should be copied first

        :raises UnableToAccessException: if the file could not be accessed

        :param file:    File object instance to update
        :param content: bytes to load in the file
        :return:        None
        """
        self.LOGGER.info(f"Updating {file.path} content")
        try:
            with open(file.path, "wb") as f:
                f.write(content)
        except (OSError, PermissionError):
            self.LOGGER.error(f"Unable to update {file.path} contents")
            raise UnableToAccessException(file.path)

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
            with open(new_file_path, "wb") as f:
                size = f.write(file.get_content())
            os.utime(new_file_path, (file.modified, file.modified))
        except (PermissionError, OSError):
            self.LOGGER.warning(f"Cant create a file {new_file_path}")
            raise UnableToAccessException(new_file_path)

        self.LOGGER.info(f"Created new file at {new_file_path}")
        uploaded_file = File(
            path=f"{remote_folder.path}/{file.name}",
            handler=self,
            stat={
                "modified": file.modified,
                "size": size,
                "id": os.stat(new_file_path).st_ino
            }
        )
        return uploaded_file

    def upload_folder(self, folder: Folder, new_folder_path: str, with_content: bool = False) -> Folder:
        """
        Copies the specified Folder object instance into a remote path
        Copies the contents of the folder if needed

        Uses os.makedirs() to create folders
        Uses upload_file() to upload file as contents of a folder
        Preserves file modification date

        :raises NoBasePathSpecifiedException: if the folder base path is not specified
        :raises UnableToAccessException: if the folder cannot be accessed

        :param folder:          Folder object instance to copy from
        :param new_folder_path: string path to copy to
        :param with_content:    whether to copy folder contents
        :return: newly created  Folder object instance
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
            os.makedirs(new_folder_path)
            os.utime(new_folder_path, (folder.modified, folder.modified))
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

    def get_folder_content(self, folder: Folder) -> List[Union[Folder, File]]:
        """
        Gets the folder content in a form of files and folders
        :param folder: Folder object instance
        :return: List of File and Folder objects

        Uses os.listdir to inquire folder contents
        Uses os.path.isfile to distinguish files and folders
        """

        self.LOGGER.debug(f"Getting folder content at {folder.path}")
        records = []
        for record_path in os.listdir(folder.path):
            if self.validate(record_path):
                try:
                    record_path = f"{folder.path}/{record_path}"
                    if os.path.isfile(record_path):
                        records.append(File(
                            record_path,
                            self
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
