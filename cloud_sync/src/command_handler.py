from logging import Logger
from src.clients.logger_ui import LoggerUi
from src.sync.file_sync_service import FileSyncronizationService
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class CommandHandler:
    _COMMAND_DOWNLOAD = 'download'
    _COMMAND_UPLOAD = 'upload'
    _COMMAND_SYNC = 'sync'

    def __init__(self, sync_service: FileSyncronizationService, ui: LoggerUi, logger: Logger):
        self._sync_service = sync_service
        self._ui = ui
        self._logger = logger

    def handle(self, command: str, cloud_path: str):
        match command:
            case self._COMMAND_DOWNLOAD: self.__sync(cloud_path, download=True, upload=False)
            case self._COMMAND_UPLOAD: self.__sync(cloud_path, download=False, upload=True)
            case self._COMMAND_SYNC: self.__sync(cloud_path, download=True, upload=True)
            case _:
                self._logger.error('Unknown action in configuration')
                raise NotImplementedError

    def __sync(self, cloud_path: str, download: bool, upload: bool):
        self._ui.output('Synchronizing {} cloud folder'.format(cloud_path))
        self._ui.output('Download files {}'.format(download))
        self._ui.output('Upload files {}'.format(upload))

        files = self._sync_service.map_folder(cloud_path)
        if download:
            self.__download_from_cloud(files.download)
        if upload:
            self.__upload_to_cloud(files.upload)

    def __upload_to_cloud(self, local_files: list[LocalFileMetadata]):
        if local_files:
            self._ui.message('Upload files\n - {}'.format(self.__get_file_names(local_files)))
            if self._ui.confirm('Do you want to Upload {} files above from {}?'.format(
                len(local_files), self._sync_service.local_root), True):
                self._sync_service.upload_files(local_files)
            else:
                self._ui.message('upload files cancelled')
        else:
            self._ui.message('nothing to upload')

    def __get_file_names(self, files: list):
        return '\n - '.join(map(str, files))

    def __download_from_cloud(self, cloud_files: list[CloudFileMetadata]):
        if cloud_files:
            self._ui.message('Download files\n - {}'.format(self.__get_file_names(cloud_files)))
            if self._ui.confirm('Do you want to Download {} files above to {}?'.format(
                len(cloud_files), self._sync_service.local_root), True):
                self._sync_service.download_files(cloud_files)
            else:
                self._ui.message('download files cancelled')
        else:
            self._ui.message('nothing to download')
