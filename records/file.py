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
    def __init__(self, path, handler):
        super().__init__()
        self.handler = handler
        file_dict = self.handler.get_file_stat(path)
        self.id = file_dict.get("id")
        self.name = file_dict.get("name")
        self.location = file_dict.get("location")
        self.format_ = file_dict.get("format")
        self.size = file_dict.get("size")
        self.modified = file_dict.get("modified")

    def get_dict(self):
        """
        Returns basis information about the file
        Overrides BaseRecord method
        adds format value

        :return: dictionary about the file
        """
        info_dict = super().get_dict()
        info_dict["format"] = self.format_
        return info_dict

    def get_full_path(self):
        """
        Returns path of a file
        :return:
        """
        path = f"{self.location}/{self.name}"
        if self.format_ != "no format":
            path += f".{self.format_}"
        return path

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

    def copy(self, remote_handler, remote_location):
        """
        Copyies the file into a remote location
        Uses remote handler to create and store file
        :param remote_handler: remote handler to handle file creation
        :param remote_location: remote path used to save a file
        :return: newly create file
        """
        new_file = remote_handler.upload_file(self, remote_location)
        return new_file

    def __str__(self):
        return f"Type: File\n" \
               f"Lctn: {self.get_full_path()}\n" \
               f"Name: {self.name}\n" \
               f"Frmt: {self.format_}\n" \
               f"Size: {self.size}\n" \
               f"Crtd: {self.modified}\n"
