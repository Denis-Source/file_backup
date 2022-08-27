import datetime
import time

from handlers.g_drive_handler import GDriveHandler
from handlers.local_handler import LocalHandler
from handlers.sftp_handler import SFTPHandler
from records.folder import Folder

from validator import Validator
from logger import Logger


class Console:
    """
    Console add-on to backup files
    """
    LOCAL_HANDLER = LocalHandler.HANDLER_NAME
    SFTP_HANDLER = SFTPHandler.HANDLER_NAME
    GDRIVE_HANDLER = GDriveHandler.HANDLER_NAME

    HANDLERS = {
        LOCAL_HANDLER: LocalHandler,
        SFTP_HANDLER: SFTPHandler,
        GDRIVE_HANDLER: GDriveHandler
    }

    def __init__(self, input_handler, output_handler, input_path, output_path, validation):
        """
        :param input_handler:   name of the input handler
        :param output_handler:  name of the output handler
        :param input_path:      path of the input folder
        :param output_path:     path of the output folder
        :param validation:      bool whether to use configured validations

        :raises Exception:      if no proper handler is specified
        """
        self.logger = Logger("app")

        self.validation = validation

        if not self.validation:
            validators = []
        else:
            validators = [Validator.format_validator, Validator.name_validator]

        self.input_handler = self.HANDLERS.get(input_handler)(validators)
        self.output_handler = self.HANDLERS.get(output_handler)(validators)

        print(self.input_handler, self.output_handler)

        if not self.input_handler and not self.output_handler:
            raise Exception(f"Only the following handlers should be provided: {', '.join(self.HANDLERS.keys())}")

        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        """
        Runs the backup procedures
        :return: None
        """
        start_time = time.time()

        self.logger.info(
            f"Backuping files from {self.input_path} "
            f"using {self.input_handler.HANDLER_NAME} "
            f"to {self.output_path} "
            f"using {self.input_handler.HANDLER_NAME} "
            f"{'using' if self.validation else 'not using'} "
            f"validators"
        )

        input_folder = Folder(self.input_path, self.input_handler, self.input_path)
        input_folder.set_content()

        input_folder.copy(self.output_path, self.output_handler, with_content=True)

        total_seconds = round(time.time() - start_time)
        self.logger.info(f"Done in {datetime.timedelta(seconds=total_seconds)}!")
