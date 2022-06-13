from abc import ABC, abstractmethod


class BaseRecord(ABC):
    """
    Base Record class
    Defines basic structure of records (files or folders)

    Attributes:
        location    path of the record
        name        name of the record
        modified    last time modified
        size        size of a record
        id          unique id of a record
    """

    def __init__(self):
        self.location = None
        self.name = None
        self.modified = None
        self.size = None
        self.id = None

    @abstractmethod
    def set_stat(self) -> None:
        pass

    @abstractmethod
    def copy(self, remote_location, remote_handler):
        """
        Should copy the record into a specified location
        Should use the specified handler

        :param remote_location: remote location
        :param remote_handler:  handler to copy
        :return: newly created record
        """
        pass

    def get_dict(self):
        """
        Returns basic information about the record
        :return: dictionary about the record
        """
        return {
            "type": self.__class__.__name__,
            "name": self.name,
            "size": self.size,
            "modified": self.modified,
            "id": self.id
        }
