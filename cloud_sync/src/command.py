from logging import Logger
from src.clients.ui import UI
from src.services.file_sync_service import FileSyncronizationService
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore

class CommandRunner:
    def __init__(self, localStore: LocalFileStore, cloudStore: CloudStore, syncService: FileSyncronizationService, ui: UI, logger: Logger):
        self.localStore = localStore
        self.cloudStore = cloudStore
        self.syncService = syncService
        self.ui = ui
        self.logger = logger

    def run(self, command:str, cloud_path: str):
        match command:
            case 'download': self.__sync(cloud_path, download=True, upload=False)
            case 'upload': self.__sync(cloud_path, download=False, upload=True)
            case 'sync': self.__sync(cloud_path, download=True, upload=True)
            case _:
                self.logger.error('Unknown action in configuration')
                raise NotImplementedError

    def __sync(self, cloud_path: str, download: bool, upload: bool):
        self.ui.message('Synchronizing {} cloud folder'.format(cloud_path))
        self.ui.message('Download files {}'.format(download))
        self.ui.message('Upload files {}'.format(upload))

        download_files, upload_files = self.syncService.map_recursive(cloud_path)
        if download: self.__download_from_cloud(download_files)
        if upload: self.__upload_to_cloud(upload_files)

    def __upload_to_cloud(self, cloud_paths: list):
        if cloud_paths:
            self.ui.message('=== Upload files\n - {}'.format('\n - '.join(map(str, cloud_paths))))
            if self.ui.confirm('Do you want to Upload {} files above from {}?'.format(len(cloud_paths), self.localStore.get_absolute_path("/")), True):
                for cloud_path in cloud_paths:
                    local_path = self.localStore.get_absolute_path(cloud_path)
                    self.logger.info('uploading {} => {} ...'.format(local_path, cloud_path))
                    self.__upload_file(local_path, cloud_path, overwrite=True)
            else:
                self.ui.message('=== upload files cancelled')
        else:
            self.ui.message('=== nothing to upload')

    def __download_from_cloud(self, cloud_paths: list):
        if cloud_paths:
            self.ui.message('=== Download files\n - {}'.format('\n - '.join(map(str, cloud_paths))))
            if self.ui.confirm('Do you want to Download {} files above to {}?'.format(len(cloud_paths), self.localStore.get_absolute_path("/")), True):
                for cloud_path in cloud_paths:
                    self.logger.info('downloading {} => {} ...'.format(cloud_path, self.localStore.get_absolute_path(cloud_path)))
                    res, cloud_md = self.cloudStore.read(cloud_path)
                    self.logger.debug('downloaded file: {}'.format(cloud_md))
                    self.localStore.save(cloud_path, res.content, cloud_md.client_modified)
            else:
                self.ui.message('=== download files cancelled')
        else:
            self.ui.message('=== nothing to download')

    def __upload_file(self, local_path: str, cloud_path: str, overwrite: bool):
        self.logger.debug('local_path={}, cloud_path={}'.format(local_path, cloud_path))
        content, local_md = self.localStore.read(local_path)
        self.cloudStore.save(cloud_path, content, local_md, overwrite)
