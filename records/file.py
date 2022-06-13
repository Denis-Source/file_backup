from __future__ import annotations
from pathlib import Path

from records.base_record import BaseRecord


class File(BaseRecord):
    """
    File class
    Represents file in a filesystem in a form of an instance
    Inherits from BaseRecord class

    Stores information about the file
    Attributes:
        handler     handler to manipulate a real file
        name        name of a file
        location    real file path
        format_     format of a file
        modified    last time of a file
        size        size of a file
        id          unique id of a record

    """

    def __init__(self, path, handler, stat: dict = None):
        super().__init__()
        path_obj = Path(path)

        self.handler = handler
        self.path = path

        self.name = path_obj.name
        self.format_ = path_obj.suffix

        self.set_stat(stat)

    def set_stat(self, stat: dict = None):
        if not stat:
            stat = self.handler.get_file_stat(self.path)

        self.id = stat.get("id")
        self.size = stat.get("size")
        self.modified = stat.get("modified")

    def get_dict(self) -> dict:
        """
        Returns basis information about the file
        Overrides BaseRecord method
        adds format value

        :return: dictionary about the file
        """
        stat = super().get_dict()
        stat["format"] = self.format_
        return stat

    def get_content(self) -> bytes:
        """
        Returns file content of a file

        :return: bytes of the file
        """
        return self.handler.get_file_content(self)

    def set_content(self, content: bytes) -> None:
        """
        Sets content of a file
        :param content: bytes
        :return: None
        """
        self.handler.set_file_content(self, content)

    def copy(self, remote_handler, remote_location) -> File:
        """
        Copies the file into a remote location
        Uses remote handler to create and store file
        :param remote_handler: remote handler to handle file creation
        :param remote_location: remote path used to save a file
        :return: newly create file
        """
        new_file = remote_handler.upload_file(self, remote_location)
        return new_file

    def __str__(self):
        return f"Type: File\n" \
               f"Lctn: {self.path}\n" \
               f"Name: {self.name}\n" \
               f"Frmt: {self.format_}\n" \
               f"Size: {self.size}\n" \
               f"Modf: {self.modified}\n" \
               f"Id:   {self.id}\n"
