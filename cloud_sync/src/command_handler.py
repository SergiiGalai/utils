from logging import Logger
from src.clients.command_ui import CommandHandlerUi
from src.sync.file_sync_service import FileSyncronizationService
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class CommandHandler:
    _COMMAND_DOWNLOAD = 'download'
    _COMMAND_UPLOAD = 'upload'
    _COMMAND_SYNC = 'sync'

    def __init__(self, sync_service: FileSyncronizationService, ui: CommandHandlerUi, logger: Logger):
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
        self._ui.sync(cloud_path, download, upload)
        files = self._sync_service.map_folder(cloud_path)
        if download:
            self.__download_from_cloud(files.download)
        if upload:
            self.__upload_to_cloud(files.upload)

    def __upload_to_cloud(self, local_files: list[LocalFileMetadata]):
        if local_files:
            ui_files = [f.cloud_path for f in local_files]
            self._ui.upload_to_cloud(ui_files,
                                     self._sync_service.local_root,
                                     lambda: self._sync_service.upload_files(local_files))
        else:
            self._ui.upload_nothing()

    def __download_from_cloud(self, cloud_files: list[CloudFileMetadata]):
        if cloud_files:
            ui_files = [f.cloud_path for f in cloud_files]
            self._ui.download_from_cloud(ui_files,
                                         self._sync_service.local_root,
                                         lambda: self._sync_service.download_files(cloud_files))
        else:
            self._ui.download_nothing()
