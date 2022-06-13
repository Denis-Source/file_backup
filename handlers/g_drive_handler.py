import datetime
import os
from typing import Union, List
import io

import googleapiclient
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from errors import NoBasePathSpecifiedException, UnableToAccessException, RecordNotFoundException
from handlers.base_handler import BaseHandler

from logger import Logger

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from records.file import File
from records.folder import Folder


class GDriveHandler(BaseHandler):
    """
    Google Drive APIv3 Handler class
    Inherits from BaseHandler

    Constants:
        SCOPES              scopes of API to be able to read/write remote files
        CREDENTIALS_FILE    file that stores credentials needed for API
        TOKEN_FILE          file that stores token (to allow automatic login)
        HANDLER_NAME        name of the handler
        LOGGER              logger instance
    """

    SCOPES = ["https://www.googleapis.com/auth/drive"]
    CREDENTIALS_FILE = "client_secrets.json"
    TOKEN_FILE = "token.json"
    HANDLER_NAME = "gdrive handler"
    LOGGER = Logger(HANDLER_NAME)

    def __init__(self):
        super().__init__()
        self._credentials = None
        self._connection = None
        self._authenticate()

    def _authenticate(self) -> None:
        """
        Authenticates client with Google Drive API
        Uses credentials file
        Opens browser for account selection
        Stores a token to save a session
        :return:
        """
        if os.path.exists('token.json'):
            self._credentials = Credentials.from_authorized_user_file('token.json', self.SCOPES)

        if not self._credentials or not self._credentials.valid:
            if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                self._credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS_FILE, self.SCOPES)
                self._credentials = flow.run_local_server(port=0)
            with open(self.TOKEN_FILE, 'w') as token:
                token.write(self._credentials.to_json())
        try:
            self._connection = build('drive', 'v3', credentials=self._credentials)
        except HttpError as error:
            self.LOGGER.critical(f"An error occurred during the authentication: {error}")

    def _find_files_in_folder(self, folder_id: str, record_name: str) -> List[dict]:
        """
        Checks whether the folder contains files with a specified name
        :param folder_id:       folder id to search in
        :param record_name:     record name to search
        :return:                list of records (dictionaries)
        """
        self.LOGGER.debug(f"Finding records with name {record_name} in folder {folder_id}")
        try:
            response = self._connection.files().list(
                q=f"name = '{record_name}' and '{folder_id}' in parents",
                fields=f"files(id, name, size, modifiedTime)",
            ).execute()

        except googleapiclient.errors.HttpError:
            self.LOGGER.warning(f"Cannot access folder with id {folder_id}")
            raise UnableToAccessException(folder_id)

        records = response.get('files', [])
        self.LOGGER.info(f"Found records with name {record_name} in folder {folder_id}: {len(records)}")
        if records:
            return records
        else:
            return []

    def get_file_stat(self, path: str) -> dict:
        """
        Returns the following stats about the specified file
        in a form of a dictionary:
            modified
            size
            id

        :raises RecordNotFoundException: if the file could not be found

        :param path: location of the file
        :return: dictionary with the specified information
        """
        self.LOGGER.debug(f"Getting info about the file of {path}")

        file_name = path.split("/")[-1]
        location = "/".join(path.split("/")[:-1])

        if location:
            root_id = self.get_folder_stat(location)["id"]
        else:
            root_id = self._connection.files().get(fileId="root").execute()["id"]

        response = self._connection.files().list(
            q=f"name = '{file_name}' and '{root_id}' in parents",
            fields=f"files(id, name, size, modifiedTime)",
        ).execute()

        records = response.get('files', [])

        if not records:
            self.LOGGER.warning(f"File not found of {path}")
            raise RecordNotFoundException(path)

        self.LOGGER.info(f"Got file id of {path}: {records[0]['id']}")

        dt = datetime.datetime.strptime(records[0].get("modifiedTime"), "%Y-%m-%dT%H:%M:%S.%f%z")
        modified = dt.timestamp()

        return {
            "size": records[0].get("size"),
            "modified": modified,
            "id": records[0].get("id")
        }

    def get_folder_stat(self, path: str) -> dict:
        """
        Returns the following stats about the specified folder
        in a form of a dictionary:
            created
            size
            id
        Due to the nature of the way how google drive stores file structure
        Iterates over the folders in the specified path
        From a parent to a child
        """

        self.LOGGER.debug(f"Getting info about the file of {path}")

        # gets a list of folders (from root to a specified one)
        folders_names = path.split("/")

        # gets a root folder id as a start point
        root_id = self._connection.files().get(fileId="root").execute()["id"]

        self.LOGGER.info(f"Got id about the root folder: {root_id}")
        response = None

        while folders_names:
            # gets the first folder from a list
            # and removes it
            folder_name = folders_names.pop(0)
            self.LOGGER.debug(f"Getting id about the folder {folder_name}")

            # gets information about the current folder
            try:
                response = self._connection.files().list(
                    q=f"name = '{folder_name}' and '{root_id}' in parents",
                    fields=f"files(id, name, modifiedTime)",
                ).execute()
            except googleapiclient.errors.HttpError:
                self.LOGGER.error(f"Error getting info about folder {folder_name}")
                raise RecordNotFoundException(path)
        else:
            # when the folder list is exhausted
            # gets the stored information about the last folder
            # (needed folder)
            records = response.get('files', [])

            # if response is empty raises an exception
            if not records and response:
                self.LOGGER.warning(f"File not found at {path}")
                raise RecordNotFoundException(path)

            # due to the way how Google Drive api stores date
            # converts it to the epoc time
            dt = datetime.datetime.strptime(records[0].get("modifiedTime"), "%Y-%m-%dT%H:%M:%S.%f%z")
            modified = dt.timestamp()

            return {
                "size": 0,
                "modified": modified,
                "id": records[0]["id"]
            }

    def get_file_content(self, file: File) -> bytes:
        """
        Returns file content in bytes
        Uses MediaIoBaseDownload to avoid creating a temporary file
        Downloads file contents in memory using BytesIO()

        :raises UnableToAccessException: if a file could not be read

        :param          file: File object instance
        :return:        file contents in bytes
        """

        self.LOGGER.debug(f"Getting file content at {file.path}")
        try:
            request = self._connection.files().get_media(fileId=file.id)
            self.LOGGER.info(f"Request to read file {file.path} is successful")
        except googleapiclient.errors.HttpError:
            raise UnableToAccessException(file.path)

        self.LOGGER.info(f"Downloading file in memory")
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        self.LOGGER.info("Download is successful")
        file.seek(0)
        return file.read()

    def upload_file(self, file: File, remote_folder: Folder) -> File:
        """
        Copies the specified file into a remote folder
        uses MediaIoBaseUpload to avoid creating temporary files

        :raises UnableToAccessException: if a file cannot be uploaded

        :param file:            File object instance
        :param remote_folder:   Folder object instance

        :return: new File instance
        """

        self.LOGGER.debug(f"Uploading file from {file.path} to {remote_folder.path}")

        self.LOGGER.debug(f"Searching for identical files")
        files_to_replace_id = self._find_files_in_folder(remote_folder.id, f"{file.name}")

        if files_to_replace_id:
            for file_info in files_to_replace_id:
                self.LOGGER.info(f"Deleting identical file {file_info['name']}")
                self._connection.files().delete(fileId=file_info["id"]).execute()

        file_content = io.BytesIO(file.get_content())

        self.LOGGER.debug(f"Uploading virtual file to folder with id {remote_folder.id}")

        # mimetype is set to application/binary as it is universal
        # and Google Drive api sets it automatically anyways
        downloader = MediaIoBaseUpload(file_content, mimetype="application/binary")

        # some metadata is required to store files appropriately
        # to store file in a folder
        # specifies parent folder id
        file_metadata = {
            "name": file.name,
            "parents": [remote_folder.id],
        }

        # as the file is stored
        # file information is created
        file_info = self._connection.files().create(body=file_metadata, media_body=downloader,
                                                    fields=f"id, name, size, modifiedTime", ).execute()

        # due to the way how Google Drive api stores date
        # converts it to the epoc time
        dt = datetime.datetime.strptime(file_info.get("modifiedTime"), "%Y-%m-%dT%H:%M:%S.%f%z")
        modified = dt.timestamp()

        return File(
            path=f"{remote_folder.path}/{file.name}",
            handler=self,
            stat={
                "modified": modified,
                "size": file_info.get("size"),
                "id": file_info.get("id"),
            }
        )

    def _create_folder(self, folder_name: str, parent_folder: Folder = None) -> Folder:
        """
        Creates folder in a specified folder

        Due to the nature of a Google Drive API file structure
        It is not that trivial to create nested folders

        If the parent folder parameter is not set
        created folder in the root folder

        :param folder_name:     new folder name
        :param parent_folder:   parent folder
        :return:                newly created Folder object instance
        """
        # TODO modification parameter is not set
        if not parent_folder:
            parent_id = self._connection.files().get(fileId="root").execute()["id"]
            location = ""
        else:
            parent_id = parent_folder.id
            location = parent_folder.path

        self.LOGGER.debug(f"Creating folder {folder_name} at {location}")
        folders_to_replace_id = self._find_files_in_folder(parent_id, folder_name)

        # Checks whether the specified folder already exists
        # if so returns it
        if folders_to_replace_id:
            self.LOGGER.info(f"Folder {folder_name} is already exists at {location}")
            return Folder(
                path=f"{location}/{folder_name}",
                handler=self,
                stat={
                    # "modified": folder_modified,
                    "size": 0,
                    "id": folders_to_replace_id[0].get("id"),
                }
            )

        # Otherwise creates metadata
        # To define the folder type
        # mimeType of application/vnd.google-apps.folder is used
        # parent folder id is also used

        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            # "modifiedTime": int(folder_modified),
            "parents": [parent_id]
        }

        # creates folder stores response as it contains the id of the folder
        try:
            response = self._connection.files().create(body=folder_metadata,
                                                       fields='id').execute()
        except googleapiclient.errors.HttpError:
            raise UnableToAccessException(folder_name)

        self.LOGGER.info(f"Created folder {folder_name} at {location}")

        return Folder(
            path=f"{location}/{folder_name}",
            handler=self,
            stat={
                # "modified": int(folder_modified),
                "size": 0,
                "id": response.get("id")
            }
        )

    def upload_folder(self, folder: Folder, new_folder_path: str, with_content: bool = False) -> Folder:
        """
        Copies the specified Folder object instance into a remote path
        Copies the contents of the folder if needed

        Recursively creates folders and fills them with files
        if with_content flag is set

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

        prev_folder_path = new_folder_path
        new_folder_path = f"{new_folder_path}{folder_relative_path}"

        folder_paths = new_folder_path.split("/")

        new_folder = None
        self.LOGGER.info(f"Creating folder at {new_folder_path}")

        for folder_path in folder_paths:
            new_folder = self._create_folder(folder_path, new_folder)

        if with_content:
            for path, record in folder.children.items():
                if self.validate(path):
                    self.LOGGER.info(f"Сopying {record.__class__.__name__} at {record.path}")
                    try:
                        if isinstance(record, File):
                            file = self.upload_file(record, new_folder)
                            new_folder.add_child(file)
                        else:
                            folder = self.upload_folder(record, prev_folder_path, with_content=True)
                            new_folder.add_child(folder)
                    except UnableToAccessException:
                        self.LOGGER.warning(f"Cant create a child record in folder {folder.path}")
                else:
                    self.LOGGER.info(f"{path} is not validated, skipping")
        return new_folder

    def get_folder_content(self, folder) -> List[Union[Folder, File]]:
        """
        Gets the folder content in a form of a list of files and folders

        :param folder: Folder object instance
        :return: List of File and Folder objects

        """
        self.LOGGER.debug(f"Getting contents of the folder at {folder.path}")
        response = self._connection.files().list(
            q=f"'{folder.id}' in parents",
            fields=f"files(id, name, modifiedTime, mimeType, size)",
        ).execute()

        records_info = response.get('files', [])

        records = []

        for record_info in records_info:
            record_path = f"{folder.path}/{record_info['name']}"

            dt = datetime.datetime.strptime(record_info.get("modifiedTime"), "%Y-%m-%dT%H:%M:%S.%f%z")
            modified = dt.timestamp()

            record_dict = {
                "modified": modified,
                "size": record_info.get("size"),
                "id": record_info.get("id"),
            }
            # to check record type
            # uses record mime type

            if record_info["mimeType"] == "application/vnd.google-apps.folder":
                records.append(Folder(
                    path=record_path,
                    handler=self,
                    base_path=folder.base_location,
                    stat=record_dict
                ))
            else:
                records.append(File(
                    path=record_path,
                    handler=self,
                    stat=record_dict
                ))
        return records

    def set_file_content(self, file: File, content: bytes):
        pass