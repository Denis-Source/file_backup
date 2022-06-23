# # from handlers.local_handler import LocalHandler
# # from handlers.sftp_handler import SFTPHandler
# # from handlers.g_drive_handler import GDriveHandler
# #
# # from records.file import File
# # from records.folder import Folder
# #
# # from validator import Validator
# from backup_app import BackUpApp
from handlers.local_handler import LocalHandler
from records.folder import Folder

if __name__ == '__main__':
    # BackUpApp().run()

#     validators = [Validator.format_validator, Validator.name_validator]
#
    input_folder_path = r"C:/Games/Besiege v1.10"
    # output_folder_path = "game"

    input_handler = LocalHandler()
    input_folder = Folder(input_folder_path, input_handler, input_folder_path)

    input_folder.set_content()
    print()
    #
    # output_handler = GDriveHandler()
    # input_folder.copy(output_folder_path, output_handler, with_content=True)