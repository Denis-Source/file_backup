from handlers.local_handler import LocalHandler
from handlers.sftp_handler import SFTPHandler
from handlers.g_drive_handler import GDriveHandler

from records.file import File
from records.folder import Folder

from validator import Validator

if __name__ == '__main__':
    # validators = [Validator.format_validator, Validator.name_validator]
    validators = []

    input_folder_path = "C:/Games/Besiege v1.10"
    output_folder_path = "testing"

    input_handler = LocalHandler(validators=validators)
    input_folder = Folder(input_folder_path, input_handler, input_folder_path)

    input_folder.set_content()
    output_handler = GDriveHandler()

    output_folder = input_folder.copy(output_folder_path, output_handler, with_content=True)
    output_folder.dump_structure()
