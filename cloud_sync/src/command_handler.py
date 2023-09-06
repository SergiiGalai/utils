from logging import Logger
from src.clients.logger_ui import LoggerUi
from src.services.file_sync_service import FileSyncronizationService
from src.stores.models import CloudFileMetadata, LocalFileMetadata


class CommandHandler:
    COMMAND_DOWNLOAD = 'download'
    COMMAND_UPLOAD = 'upload'
    COMMAND_SYNC = 'sync'

    def __init__(self, sync_service: FileSyncronizationService, ui: LoggerUi, logger: Logger):
        self._sync_service = sync_service
        self._ui = ui
        self._logger = logger

    def handle(self, command: str, cloud_path: str):
        match command:
            case self.COMMAND_DOWNLOAD: self.__sync(cloud_path, download=True, upload=False)
            case self.COMMAND_UPLOAD: self.__sync(cloud_path, download=False, upload=True)
            case self.COMMAND_SYNC: self.__sync(cloud_path, download=True, upload=True)
            case _:
                self._logger.error('Unknown action in configuration')
                raise NotImplementedError

    def __sync(self, cloud_path: str, download: bool, upload: bool):
        self._ui.output('Synchronizing {} cloud folder'.format(cloud_path))
        self._ui.output('Download files {}'.format(download))
        self._ui.output('Upload files {}'.format(upload))

        map_files = self._sync_service.map_files(cloud_path)
        if download:
            self.__download_from_cloud(map_files.download)
        if upload:
            self.__upload_to_cloud(map_files.upload)

    def __upload_to_cloud(self, local_files: list[LocalFileMetadata]):
        if local_files:
            self._ui.message(
                'Upload files\n - {}'.format('\n - '.join(map(str, local_files))))
            if self._ui.confirm('Do you want to Upload {} files above from {}?'.format(len(local_files), self._sync_service.local_root), True):
                self._sync_service.upload_files(local_files)
            else:
                self._ui.message('upload files cancelled')
        else:
            self._ui.message('nothing to upload')

    def __download_from_cloud(self, cloud_files: list[CloudFileMetadata]):
        if cloud_files:
            self._ui.message(
                'Download files\n - {}'.format('\n - '.join(map(str, cloud_files))))
            if self._ui.confirm('Do you want to Download {} files above to {}?'.format(len(cloud_files), self._sync_service.local_root), True):
                self._sync_service.download_files(cloud_files)
            else:
                self._ui.message('download files cancelled')
        else:
            self._ui.message('nothing to download')
