from src.clients.console_ui import ConsoleUi
from logging import Logger


class CommandHandlerUi:
    def __init__(self, ui: ConsoleUi, logger: Logger):
        self._ui = ui
        self._logger = logger

    def sync(self, cloud_path: str, download: bool, upload: bool):
        self._ui.output('Synchronizing {} cloud folder'.format(cloud_path))
        self._ui.output('Download files {}'.format(download))
        self._ui.output('Upload files {}'.format(upload))

    def upload_to_cloud(self, files: list[str], local_root: str, upload_handler):
        self._ui.message('Upload files\n - {}'.format(self.__to_string(files)))
        question = 'Do you want to Upload {} files above from {}?'.format(len(files), local_root)
        if self._ui.confirm(question, True):
            upload_handler()
        else:
            self._ui.message('upload files cancelled')

    def upload_nothing(self):
        self._ui.message('nothing to upload')

    def __to_string(self, files: list):
        return '\n - '.join(map(str, files))

    def download_from_cloud(self, cloud_files: list[str], local_root: str, download_handler):
        self._ui.message('Download files\n - {}'.format(self.__to_string(cloud_files)))
        question = 'Do you want to Download {} files above to {}?'.format(len(cloud_files), local_root)
        if self._ui.confirm(question, True):
            download_handler()
        else:
            self._ui.message('download files cancelled')

    def download_nothing(self):
        self._ui.message('nothing to download')
