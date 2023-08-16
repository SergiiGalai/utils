from logging import Logger
from ui import UI
from file_store import FileStore
from file_mapper import FileMapper
from dropbox_store import DropboxStore

class Controller:
    def __init__(self, fileStore: FileStore, dboxStore: DropboxStore, fileMapper: FileMapper, ui: UI, logger: Logger):
        self.fileStore = fileStore
        self.dboxStore = dboxStore
        self.fileMapper = fileMapper
        self.ui = ui
        self.logger = logger

    def sync(self, dbox_path: str, download: bool, upload: bool):
        self.ui.message('Synchronizing {} dropbox folder'.format(dbox_path))
        self.ui.message('Download files {}'.format(download))
        self.ui.message('Upload files {}'.format(upload))
        download_files, upload_files = self.fileMapper.map_recursive(dbox_path)
        if download: self.__download_from_dropbox(download_files)
        if upload: self.__upload_to_dropbox(upload_files)

    def __upload_to_dropbox(self, dbx_paths: list):
        if dbx_paths:
            self.ui.message('=== Upload files\n - {}'.format('\n - '.join(map(str, dbx_paths))))
            if self.ui.confirm('Do you want to Upload {} files above from {}?'.format(len(dbx_paths), self.fileStore.get_absolute_path("/")), True):
                for dbox_path in dbx_paths:
                    local_path = self.fileStore.get_absolute_path(dbox_path)
                    self.logger.info('uploading {} => {} ...'.format(local_path, dbox_path))
                    self.__upload_file(local_path, dbox_path, overwrite=True)
            else:
                self.ui.message('=== upload files cancelled')
        else:
            self.ui.message('=== nothing to upload')

    def __download_from_dropbox(self, dbx_paths: list):
        if dbx_paths:
            self.ui.message('=== Download files\n - {}'.format('\n - '.join(map(str, dbx_paths))))
            if self.ui.confirm('Do you want to Download {} files above to {}?'.format(len(dbx_paths), self.fileStore.get_absolute_path("/")), True):
                for dbox_path in dbx_paths:
                    self.logger.info('downloading {} => {} ...'.format(dbox_path, self.fileStore.get_absolute_path(dbox_path)))
                    res, dbox_md = self.dboxStore.read(dbox_path)
                    self.logger.debug('downloaded file: {}'.format(dbox_md))
                    self.fileStore.save(dbox_path, res.content, dbox_md.client_modified)
            else:
                self.ui.message('=== download files cancelled')
        else:
            self.ui.message('=== nothing to download')

    def __upload_file(self, local_path: str, dbx_path: str, overwrite: bool):
        self.logger.debug('local_path={}, dbx_path={}'.format(local_path, dbx_path))
        content, local_md = self.fileStore.read(local_path)
        self.dboxStore.save(dbx_path, content, local_md, overwrite)
