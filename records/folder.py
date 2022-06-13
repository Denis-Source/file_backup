from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Union

from errors import UnableToAccessException
from records.base_record import BaseRecord
from records.file import File


class Folder(BaseRecord):
    """
    Folder class
    Represents folder in a filesystem in a form of an instance
    Inherits from BaseRecord class

    Stores information about the file
    Attributes:
        handler         handler to manipulate a real file
        modified        last time of a file
        size            size of a file
        id          unique id of a record
        base_location   needed to know the relative and absolute path
    """

    def __init__(self, path, handler, base_path=None, stat: dict = None):
        super().__init__()
        path_obj = Path(path)

        self.handler = handler
        self.path = path

        self.base_location = base_path
        self.name = path_obj.name
        self.children = dict()

        self.set_stat(stat)

    def set_stat(self, stat: dict = None) -> None:
        if not stat:
            stat = self.handler.get_folder_stat(self.path)

        self.id = stat.get("id")
        self.size = stat.get("size")
        self.modified = stat.get("modified")

    def add_child(self, record: Union[Folder, File]):
        """
        Adds the child records to the folder structure
        :param record: Folder or File object instance
        :return: None
        """
        self.children[record.path] = record

    def set_content(self):
        """
        Recursively adds children to self and nested folders
        :return: None
        """
        content = self.handler.get_folder_content(self)
        for record in content:
            self.add_child(record)
            if isinstance(record, Folder):
                record.set_content()

    def copy(self, remote_location, remote_handler, with_content=False) -> Folder:
        """
        Copies the folder into a remote location
        Uses remote handler to create and store file

        If specified copies all the content of the folder

        :param remote_location: remote path used to save a folder
        :param remote_handler:  remote handler to handle folder creation
        :param with_content:    whether to copy folder contents
        :return: newly created folder
        """
        new_folder = remote_handler.upload_folder(self, remote_location, with_content)
        return new_folder

    def get_structure(self) -> dict:
        """
        Gets the file structure of the folder recursively

        :return: file structure dictionary
        """
        structure = dict()
        structure[self.path] = dict()
        structure[self.path]["data"] = self.get_dict()
        children = []

        for path, record in self.children.items():
            if isinstance(record, Folder):
                children.append(record.get_structure())
            else:
                children.append(record.get_dict())
        structure[self.path]["children"] = children
        return structure

    def dump_structure(self, save_folder: Folder = None) -> File:
        if not save_folder:
            save_folder = self
        structure = self.get_structure()
        structure_encoded = json.dumps(structure, indent=4, ensure_ascii=False).encode("utf-8")

        file_path = f"{save_folder.path}/structure.json"

        file = File(
            path=file_path,
            handler=save_folder.handler,
            stat={
                "size": len(structure_encoded),
                "modified": time.time()
            }
        )

        file.set_content(structure_encoded)

        return file

    def __str__(self):
        return f"Type: Folder\n" \
               f"Lctn: {self.path}\n" \
               f"Name: {self.name}\n" \
               f"Size: {self.size}\n" \
               f"Modf: {self.modified}\n" \
               f"Id:   {self.id}\n"
