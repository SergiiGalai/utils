from logging import Logger
from code.clients.ui import UI
from code.files.file_store import FileStore
from code.files.file_mapper import FileMapper
from code.stores.dropbox_store import DropboxStore

class Controller:
    def __init__(self, fileStore: FileStore, cloudStore: DropboxStore, fileMapper: FileMapper, ui: UI, logger: Logger):
        self.fileStore = fileStore
        self.cloudStore = cloudStore
        self.fileMapper = fileMapper
        self.ui = ui
        self.logger = logger

    def sync(self, cloud_path: str, download: bool, upload: bool):
        self.ui.message('Synchronizing {} cloud folder'.format(cloud_path))
        self.ui.message('Download files {}'.format(download))
        self.ui.message('Upload files {}'.format(upload))
        download_files, upload_files = self.fileMapper.map_recursive(cloud_path)
        if download: self.__download_from_cloud(download_files)
        if upload: self.__upload_to_cloud(upload_files)

    def __upload_to_cloud(self, cloud_paths: list):
        if cloud_paths:
            self.ui.message('=== Upload files\n - {}'.format('\n - '.join(map(str, cloud_paths))))
            if self.ui.confirm('Do you want to Upload {} files above from {}?'.format(len(cloud_paths), self.fileStore.get_absolute_path("/")), True):
                for cloud_path in cloud_paths:
                    local_path = self.fileStore.get_absolute_path(cloud_path)
                    self.logger.info('uploading {} => {} ...'.format(local_path, cloud_path))
                    self.__upload_file(local_path, cloud_path, overwrite=True)
            else:
                self.ui.message('=== upload files cancelled')
        else:
            self.ui.message('=== nothing to upload')

    def __download_from_cloud(self, cloud_paths: list):
        if cloud_paths:
            self.ui.message('=== Download files\n - {}'.format('\n - '.join(map(str, cloud_paths))))
            if self.ui.confirm('Do you want to Download {} files above to {}?'.format(len(cloud_paths), self.fileStore.get_absolute_path("/")), True):
                for cloud_path in cloud_paths:
                    self.logger.info('downloading {} => {} ...'.format(cloud_path, self.fileStore.get_absolute_path(cloud_path)))
                    res, dbox_md = self.cloudStore.read(cloud_path)
                    self.logger.debug('downloaded file: {}'.format(dbox_md))
                    self.fileStore.save(cloud_path, res.content, dbox_md.client_modified)
            else:
                self.ui.message('=== download files cancelled')
        else:
            self.ui.message('=== nothing to download')

    def __upload_file(self, local_path: str, cloud_path: str, overwrite: bool):
        self.logger.debug('local_path={}, cloud_path={}'.format(local_path, cloud_path))
        content, local_md = self.fileStore.read(local_path)
        self.cloudStore.save(cloud_path, content, local_md, overwrite)
