from abc import ABC, abstractmethod
from typing import List, Union, Callable

from records.file import File
from records.folder import Folder


class BaseHandler(ABC):
    """
    Handler Base class
    Defines abstract methods
    """

    def __init__(self, validators: List[Callable] = None):
        if validators is None:
            validators = []
        self.validators = validators

    def validate(self, path: str):
        if self.validators:
            for validator in self.validators:
                if not validator(path):
                    return False
        return True

    @abstractmethod
    def get_file_stat(self, path: str) -> dict:
        """
        Should return the following stats about the specified file
        in a form of a dictionary:
            location
            name
            format
            modified
            size

        :param path: location of the file
        :return: dictionary with the specified information
        """
        pass

    @abstractmethod
    def get_folder_stat(self, path: str) -> dict:
        """
        Should return the following stats about the specified folder
        in a form of a dictionary:
            location
            name
            created
            size

        :param path: location of the folder
        :return: dictionary with the specified information
        """
        pass

    @abstractmethod
    def get_file_content(self, file: File) -> bytes:
        """
        Should return file content in bytes
        :param file: File object instance
        :return: bytes
        """
        pass

    @abstractmethod
    def upload_file(self, file: File, remote_folder: Folder) -> File:
        """
        Should copy the specified file into a remote folder

        :param file: File object instance
        :param remote_folder: Folder object instance
        :return: new File instance
        """
        pass

    @abstractmethod
    def upload_folder(self, folder: Folder, new_folder_path: str, with_content: bool = False) -> Folder:
        """
        Should copy the specified Folder object instance into a remote path
        Should copy the contents of the folder if needed

        :param folder: Folder object instance to copy from
        :param new_folder_path: string path to copy to
        :param with_content: whether to copy folder contents
        :param validators: list of validators
        :return: newly created Folder object instance
        """
        pass

    @abstractmethod
    def get_folder_content(self, folder) -> List[Union[Folder, File]]:
        """
        Should get the folder content in a form of a list
        :param folder: Folder object instance
        :return: List of File and Folder objects
        """
        pass

    @abstractmethod
    def upload_structure(self, folder: Folder, content: bytes) -> File:
        """
        Should save the folder structure JSON in a specified folder

        :param folder:  Folder object instance to upload file into
        :param content: new file contents in bytes
        :return:        newly created File object instance
        """
        pass
