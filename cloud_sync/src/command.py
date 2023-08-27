from logging import Logger
from src.clients.ui import UI
from src.services.file_sync_service import FileSyncronizationService
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore

class CommandRunner:
    def __init__(self, localStore: LocalFileStore, cloudStore: CloudStore, syncService: FileSyncronizationService, ui: UI, logger: Logger):
        self._localStore = localStore
        self._cloudStore = cloudStore
        self._syncService = syncService
        self._ui = ui
        self._logger = logger

    def run(self, command:str, cloud_path: str):
        match command:
            case 'download': self.__sync(cloud_path, download=True, upload=False)
            case 'upload': self.__sync(cloud_path, download=False, upload=True)
            case 'sync': self.__sync(cloud_path, download=True, upload=True)
            case _:
                self._logger.error('Unknown action in configuration')
                raise NotImplementedError

    def __sync(self, cloud_path: str, download: bool, upload: bool):
        self._ui.output('Synchronizing {} cloud folder'.format(cloud_path))
        self._ui.output('Download files {}'.format(download))
        self._ui.output('Upload files {}'.format(upload))

        download_files, upload_files = self._syncService.map_files(cloud_path)
        if download: self.__download_from_cloud(download_files)
        if upload: self.__upload_to_cloud(upload_files)

    def __upload_to_cloud(self, cloud_paths: list):
        if cloud_paths:
            self._ui.message('Upload files\n - {}'.format('\n - '.join(map(str, cloud_paths))))
            if self._ui.confirm('Do you want to Upload {} files above from {}?'.format(len(cloud_paths), self._localStore.get_absolute_path("/")), True):
                for cloud_path in cloud_paths:
                    local_path = self._localStore.get_absolute_path(cloud_path)
                    self._logger.info('uploading {} => {} ...'.format(local_path, cloud_path))
                    self.__upload_file(local_path, cloud_path, overwrite=True)
            else:
                self._ui.message('upload files cancelled')
        else:
            self._ui.message('nothing to upload')

    def __download_from_cloud(self, cloud_paths: list):
        if cloud_paths:
            self._ui.message('Download files\n - {}'.format('\n - '.join(map(str, cloud_paths))))
            if self._ui.confirm('Do you want to Download {} files above to {}?'.format(len(cloud_paths), self._localStore.get_absolute_path("/")), True):
                for cloud_path in cloud_paths:
                    self._logger.info('downloading {} => {} ...'.format(cloud_path, self._localStore.get_absolute_path(cloud_path)))
                    cloud_content, cloud_md = self._cloudStore.read(cloud_path)
                    self._logger.debug('downloaded file: {}'.format(cloud_md))
                    self._localStore.save(cloud_path, cloud_content, cloud_md.client_modified)
            else:
                self._ui.message('download files cancelled')
        else:
            self._ui.message('nothing to download')

    def __upload_file(self, local_path: str, cloud_path: str, overwrite: bool):
        self._logger.debug('local_path={}, cloud_path={}'.format(local_path, cloud_path))
        content, local_md = self._localStore.read(local_path)
        self._cloudStore.save(cloud_path, content, local_md, overwrite)
