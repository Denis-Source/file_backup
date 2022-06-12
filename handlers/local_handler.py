import json
import os

from typing import List, Union

from handlers.base_handler import BaseHandler
from errors import NoBasePathSpecifiedException
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
            location
            name
            format
            modified
            size
            id
        Uses os.stat to access a file

        :param path: location of the file
        :return: dictionary with the specified information
        """
        self.LOGGER.debug(f"Getting information about a file at {path}")

        if not os.path.isfile(path):
            self.LOGGER.warning(f"{path} is not a file")
        stat = os.stat(path)
        name = path.split("/")[-1]
        location = "/".join(path.split("/")[:-1])
        if "." in name:
            format_ = name.split(".")[-1]
        else:
            format_ = "no_format"
        name = name[:-len(format_) - 1]
        self.LOGGER.info(f"Got information about a file at {path}")
        return {
            "location": location,
            "name": name,
            "format": format_,
            "modified": stat.st_mtime,
            "size": stat.st_size,
            "id": stat.st_ino
        }

    def get_folder_stat(self, path: str) -> dict:
        """
        Returns the following stats about the specified folder
        in a form of a dictionary:
            location
            name
            created
            size
            id
        Uses os.stat to access a folder


        :param path: location of the folder
        :return: dictionary with the specified information
        """
        self.LOGGER.debug(f"Getting information about a folder at {path}")
        if not os.path.isdir(path):
            self.LOGGER.warning(f"{path} is not a folder")
        stat = os.stat(path)
        name = path.split("/")[-1]
        location = "/".join(path.split("/")[:-1])
        self.LOGGER.info(f"Got information about a folder at {path}")
        return {
            "location": location,
            "name": name,
            "modified": stat.st_mtime,
            "size": stat.st_size,
            "id": stat.st_ino
        }

    def get_file_content(self, file: File) -> bytes:
        """
        Returns file content in bytes
        Uses open() to get file content
        # TODO file size limited with RAM

        :param file: File object instance
        :return: bytes
        """
        self.LOGGER.debug(f"Getting file content at {file.get_full_path()}")
        try:
            with open(file.get_full_path(), "rb") as f:
                self.LOGGER.info(f"File at {file.get_full_path()} is read")
                return f.read()
        except (FileNotFoundError, PermissionError):
            self.LOGGER.error(f"Cant read file {file.get_full_path()}")
            return b""

    def upload_file(self, file: File, remote_folder: Folder) -> File:
        """
        Copies the specified file into a remote folder

        :param file: File object instance
        :param remote_folder: Folder object instance
        :return: new File instance
        """

        self.LOGGER.debug(f"Uploading file from {file.get_full_path()} to {remote_folder.get_full_path()}")
        new_file_path = f"{remote_folder.get_full_path()}/{file.name}.{file.format_}"

        with open(new_file_path, "wb") as f:
            f.write(file.get_content())
        os.utime(new_file_path, (file.modified, file.modified))

        uploaded_file = File(
            path=f"{remote_folder.get_full_path()}/{file.name}.{file.format_}",
            handler=self
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

        :param folder: Folder object instance to copy from
        :param new_folder_path: string path to copy to
        :param with_content: whether to copy folder contents
        :return: newly created Folder object instance
        """

        self.LOGGER.debug(f"Uploading file from {folder.get_full_path()} to {new_folder_path}")

        if folder.base_location:
            folder_relative_path = folder.get_full_path().replace(folder.base_location, "")
        else:
            self.LOGGER.warning(f"Cant upload folder at {folder.get_full_path()}, no base path specified")
            raise NoBasePathSpecifiedException(folder.get_full_path())

        prev_folder_path = new_folder_path
        new_folder_path = f"{new_folder_path}{folder_relative_path}"
        try:
            self.LOGGER.info(f"Creating folder at {new_folder_path}")
            os.makedirs(new_folder_path)
            os.utime(new_folder_path, (folder.modified, folder.modified))
        except FileExistsError:
            self.LOGGER.info(f"Folder at {new_folder_path} is already exists")
        except OSError:
            self.LOGGER.warning(f"Cant create folder at {new_folder_path}")

        new_folder = Folder(new_folder_path, self)

        if with_content:
            self.LOGGER.debug(f"Сopying the contents of the folder at {folder.get_full_path()} to {new_folder_path}")
            for path, record in folder.children.items():

                if self.validate(path):
                    self.LOGGER.info(f"Сopying {record.__class__.__name__} at {record.get_full_path()}")
                    if isinstance(record, File):
                        try:
                            file = self.upload_file(record, new_folder)
                            new_folder.add_child(file)
                        except PermissionError:
                            self.LOGGER.warning(f"No permission to {record.get_full_path()}")
                        except FileNotFoundError:
                            self.LOGGER.warning(f"Cant access {record.get_full_path()}")
                    else:
                        folder = self.upload_folder(record, prev_folder_path, with_content=True)
                        new_folder.add_child(folder)
                else:
                    self.LOGGER.info(f"{path} is not validated, skipping")

        return new_folder

    def get_folder_content(self, folder: Folder) -> List[Union[Folder, File]]:
        """
        Gets the folder content in a form of a list
        :param folder: Folder object instance
        :return: List of File and Folder objects

        Uses os module
        """

        self.LOGGER.debug(f"Getting folder content at {folder.get_full_path()}")
        records = []
        for record_path in os.listdir(folder.get_full_path()):
            if self.validate(record_path):
                try:
                    record_path = f"{folder.get_full_path()}/{record_path}"
                    if os.path.isfile(record_path):
                        records.append(File(
                            record_path, self
                        ))
                    else:
                        records.append(Folder(
                            record_path,
                            self,
                            folder.base_location
                        ))
                except OSError:
                    self.LOGGER.warning(f"Cant access record at {record_path}")
            else:
                self.LOGGER.info(f"{record_path} is not validated, skipping")
        return records

    def dump_file_structure(self, root_folder: Folder, location) -> File:
        """
        Should save folder structure in a form of a JSON file
        :param root_folder: root Folder object instance
        :param location: path to the folder where the JSON file should be saved
        :return: newly created JSON File object instance

        Transforms dictionary into a JSON
        Uses json module
        """

        self.LOGGER.debug(f"Getting file structure of the root folder at {root_folder.get_full_path()}")
        structure = root_folder.get_structure()
        file_path = f"{location}/structure.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(structure, f, indent=4, ensure_ascii=False)
            self.LOGGER.info(f"Saved JSON structure file at {file_path}")

        return File(
            file_path,
            self
        )
