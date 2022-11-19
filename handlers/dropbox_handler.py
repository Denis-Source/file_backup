import time
from typing import List, Union, Callable

import dropbox
from dropbox.exceptions import DropboxException
from dropbox.files import FileMetadata, FolderMetadata

from config import Config
from errors import RecordNotFoundException, NotFileException, NotFolderException, NoBasePathSpecifiedException
from handlers.base_handler import BaseHandler
from logger import Logger
from records.file import File
from records.folder import Folder


class DropBoxHandler(BaseHandler):
    """
    DropBox APIv2 Handler class
    Inherits from BaseHandler
        HANDLER_NAME        name of the handler
        LOGGER              logger instance

    """
    HANDLER_NAME = "dropbox"
    LOGGER = Logger(HANDLER_NAME)

    ROOT_FOLDER_ID = "0"

    def __init__(self, validators: List[Callable] = None):
        super().__init__(validators)
        self._connection = dropbox.Dropbox(Config.DROPBOX_TOKEN)

    def get_file_stat(self, path: str) -> dict:
        """
        Returns the following stats about the specified file
        in a form of a dictionary:
            modified
            size
            id

        :raises RecordNotFoundException: if the provided path does not lead to a file
        :raises NotFileException: if the provided path does not contain a file

        :param path: location of the file
        :return: dictionary with the specified information
        """
        self.LOGGER.debug(f"Getting information about a file at {path}")

        try:
            result = self._connection.files_get_metadata(path)
            if isinstance(result, FolderMetadata):
                self.LOGGER.warning(f"{path} is not a file")
                raise NotFileException(path)

            self.LOGGER.info(f"Got information about a file at {path}")
            return {
                "size": result.size,
                "modified": result.server_modified.timestamp(),
                "id": result.id
            }

        except DropboxException:
            self.LOGGER.warning(f"File {path} not found")
            raise RecordNotFoundException(path)

    def get_folder_stat(self, path: str) -> dict:
        """
        Returns the following stats about the specified folder
        in a form of a dictionary:
            created
            size
            id
        For some reason the last modification date of the folder cannot be retrieved
        API simply does not support it

        :raises NotFolderException: if the provided path does not lead to a folder

        :param path:    path of the folder
        :return:        folder info in a form of dict
        """
        self.LOGGER.debug(f"Getting information about a folder at {path}")

        if path in ["", "/"]:
            self.LOGGER.debug(f"Dealing with root, returning dummy info")
            return {
                "size": 0,
                "modified": 0,
                "id": self.ROOT_FOLDER_ID
            }

        # to handle root path properly
        # the path should start with leading slash
        if not path.startswith("/"):
            path = f"/{path}"

        try:
            result = self._connection.files_get_metadata(path)
            if isinstance(result, FileMetadata):
                self.LOGGER.warning(f"{path} is not a folder")
                raise NotFolderException(path)

            self.LOGGER.info(f"Got information about a folder at {path}")
            return {
                "size": 0,
                "modified": 0,
                "id": result.id
            }

        except DropboxException:
            self.LOGGER.info(f"Folder {path} not found")
            raise RecordNotFoundException(path)

    def get_file_content(self, file: File) -> bytes:
        """
        Returns file content in bytes

        :raises UnableToAccessException: if a file could not be read
        :raises RecordNotFoundException: if a file could not be located

        :param          file: File object instance
        :return:        file contents in bytes
        """

        self.LOGGER.debug(f"Getting file content at {file.path}")

        try:
            metadata, response = self._connection.files_download(file.path)
            self.LOGGER.info(f"File at {file.path} is read")
            return response.content
        except DropboxException:
            self.LOGGER.error(f"Cant read file {file.path}")
            raise RecordNotFoundException(file.path)

    def upload_file(self, file: File, remote_folder: Folder) -> File:
        """
        Copies the specified file into a remote folder

        :param file:            File object instance
        :param remote_folder:   Folder object instance

        :return: new File instance
        """
        self.LOGGER.debug(f"Uploading file from {file.path} to {remote_folder.path}")

        if remote_folder.path.startswith("/"):
            leading = ""
        else:
            leading = "/"

        try:
            result = self._connection.files_upload(
                f=file.get_content(),
                path=f"{leading}{remote_folder.path}/{file.name}",
                mute=True
            )
            self.LOGGER.info(f"Uploaded file {file.path}")
            return File(
                path=f"{leading}{remote_folder.path}/{file.name}",
                handler=self,
                stat={
                    "modified": result.server_modified.timestamp(),
                    "size": result.size,
                    "id": result.id
                }
            )
        except DropboxException as e:
            self.LOGGER.warning(f"Cannot upload file {file.path}")

    def upload_folder(self, folder: Folder, new_folder_path: str, with_content: bool = False) -> Folder:
        """
        Copies the specified Folder object instance into a remote path
        Copies the contents of the folder if needed

        Recursively creates folders and fills them with files
        if with_content flag is set

        :raises NoBasePathSpecifiedException: if the folder base path is not specified

        :param folder: Folder object instance to copy from
        :param new_folder_path: string path to copy to
        :param with_content: whether to copy folder contents
        :return: newly created Folder object instance
        """
        try:
            self.LOGGER.debug(f"trying to delete already created folder")
            if folder.path.startswith("/"):
                self._connection.files_delete_v2(folder.path)
            else:
                self._connection.files_delete_v2(f"/{folder.path}")
            self.LOGGER.info(f"deleted already created folder")
        except DropboxException:
            self.LOGGER.debug(f"folder does not already exist to delete")

        if folder.base_location:
            folder_relative_path = folder.path.replace(folder.base_location, "")
        else:
            self.LOGGER.warning(f"Cant upload folder at {folder.path}, no base path specified")
            raise NoBasePathSpecifiedException(folder.path)

        new_base_folder_path = new_folder_path
        new_folder_path = f"{new_folder_path}{folder_relative_path}"

        if folder.path.startswith("/"):
            result = self._connection.files_create_folder_v2(folder.path).metadata
        else:
            result = self._connection.files_create_folder_v2(f"/{folder.path}").metadata

        new_folder = Folder(
            path=new_folder_path,
            handler=self,
            stat={
                "modified": time.time(),
                "size": 0,
                "id": result.id
            }
        )

        if folder.base_location:
            folder_relative_path = folder.path.replace(folder.base_location, "")
        else:
            self.LOGGER.warning(f"Cant upload folder at {folder.path}, no base path specified")
            raise NoBasePathSpecifiedException(folder.path)

        new_base_folder_path = new_folder_path
        new_folder_path = f"{new_folder_path}{folder_relative_path}"

        if with_content:
            for path, record in folder.children.items():
                if self.validate(path):
                    if isinstance(record, File):
                        file = self.upload_file(record, new_folder)
                        if file:
                            new_folder.add_child(file)
                    else:
                        folder = self.upload_folder(record, new_base_folder_path, with_content=True)
                        new_folder.add_child(folder)

        return new_folder

    def get_folder_content(self, folder: Folder) -> List[Union[Folder, File]]:
        """
        Gets the folder content in a form of a list of files and folders

        :param folder: Folder object instance
        :return: List of File and Folder objects
        """

        records = []
        results = self._connection.files_list_folder(folder.path)
        for entry in results.entries:
            if self.validate(entry.path_display):
                if isinstance(entry, FileMetadata):
                    records.append(File(
                        entry.path_display,
                        self
                    ))
                else:
                    records.append(Folder(
                        entry.path_display,
                        self,
                        folder.base_location
                    ))
        return records

    def upload_structure(self, folder: Folder, content: bytes) -> File:
        raise NotImplemented
