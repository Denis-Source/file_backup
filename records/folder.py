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
        name            name of a file
        location        real file path
        modified        last time of a file
        size            size of a file
        id          unique id of a record
        base_location   needed to know the relative and absolute path
    """
    def __init__(self, path, handler, base_location=None):
        super().__init__()
        self.handler = handler
        folder_dict = self.handler.get_folder_stat(path)
        self.id = folder_dict.get("id")
        self.name = folder_dict.get("name")
        self.base_location = base_location
        self.location = folder_dict.get("location")

        self.size = folder_dict.get("size")
        self.modified = folder_dict.get("modified")

        self.children = dict()

    def get_full_path(self):
        """
        Returns path of a folder
        :return:
        """

        return f"{self.location}/{self.name}"

    def add_child(self, record):
        """
        Adds the child records to the folder structure
        :param record: Folder or File object instance
        :return: None
        """
        self.children[record.get_full_path()] = record

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

    def copy(self, remote_location, remote_handler, with_content=False):
        """
        Copyies the folder into a remote location
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
        structure[self.get_full_path()] = dict()
        structure[self.get_full_path()]["data"] = self.get_dict()
        children = []

        for path, record in self.children.items():
            if isinstance(record, Folder):
                children.append(record.get_structure())
            else:
                children.append(record.get_dict())
        structure[self.get_full_path()]["children"] = children
        return structure

    def dump_structure(self, remote_location, remote_handler) -> File:
        """
        Saves file structure in a specified location
        :param remote_location: path of a remote location
        :param remote_handler:  handler to create and store file
        :return:
        """
        file = remote_handler.dump_file_structure(self, remote_location)
        return file

    def __str__(self):
        return f"Type: Folder\n" \
               f"Lctn: {self.get_full_path()}\n" \
               f"Name: {self.name}\n" \
               f"Size: {self.size}\n" \
               f"Crtd: {self.modified}\n"
