import posixpath
from logging import Logger
from src.configs.config import StorageConfig
from src.services.file_comparer_factory import FileComparerFactory
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, CloudFolderMetadata, LocalFileMetadata

class FileSyncronizationService:
    def __init__(self, localStore: LocalFileStore, cloudStore: CloudStore, config: StorageConfig, logger: Logger):
        self._localStore = localStore
        self._cloudStore = cloudStore
        self._recursive = config.recursive
        self._logger = logger
        self._file_comparer = FileComparerFactory(localStore, cloudStore, logger).create(config)
        self._logger.debug(config)

    def map_files(self, cloud_path: str) -> tuple[list[CloudFileMetadata], list[LocalFileMetadata]]:
        self._logger.info('cloud_path={}'.format(cloud_path))

        local_dirs, local_files = self._localStore.list_folder(cloud_path)
        cloud_dirs, cloud_files = self._cloudStore.list_folder(cloud_path)

        download_files, upload_files = self.__map_cloud_files_to_local(local_files, cloud_files)
        if self._recursive:
            cloud_folders = self.__map_cloud_folders_to_local(local_dirs, cloud_path, cloud_dirs)
            for cloud_folder in cloud_folders:
                download_sub, upload_sub = self.map_files(cloud_folder)
                download_files.extend(download_sub)
                upload_files.extend(upload_sub)
        else:
            self._logger.info('skipping subfolders because of configuration')
        return download_files, upload_files

    def __map_cloud_files_to_local(self, local_files: list[LocalFileMetadata], cloud_files: list[CloudFileMetadata]) -> tuple[list[CloudFileMetadata], list[LocalFileMetadata]]:
        upload_list = list[LocalFileMetadata]()
        download_list = list[CloudFileMetadata]()

        local_files_dict = {md.cloud_path.lower(): md for md in local_files} #dict
        cloud_files_dict = {md.cloud_path.lower(): md for md in cloud_files} #dict

        for key, cloud_md in cloud_files_dict.items():
            local_md = local_files_dict.get(key)
            if local_md is None:
                self._logger.info('file does NOT exist locally - {} => download list'.format(cloud_md.cloud_path))
                download_list.append(cloud_md)
            else:
                self._logger.debug('file exists locally - {}'.format(key))
                self._add_to_list_by_file_comparison(local_md, cloud_md, upload_list, download_list)

        for key, local_md in local_files_dict.items():
            if key in cloud_files_dict.keys(): continue
            self._logger.info('file NOT found on dropbox - {} => upload list'.format(local_md.local_path))
            upload_list.append(local_md)

        return download_list, upload_list

    def _add_to_list_by_file_comparison(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata,
                                        upload_list: list[LocalFileMetadata], download_list: list[CloudFileMetadata]):
        cloud_path = cloud_md.cloud_path
        if not self._file_comparer.are_equal(local_md, cloud_md):
            if local_md.client_modified > cloud_md.client_modified:
                self._logger.info('file {} has changed since last sync (cloud={} < local={}) => upload list'
                    .format(local_md.local_path, cloud_md.client_modified, local_md.client_modified))
                upload_list.append(local_md)
            else:
                self._logger.info('file {} has changed since last sync (cloud={} > local={}) => download list'
                    .format(cloud_path, cloud_md.client_modified, local_md.client_modified))
                download_list.append(cloud_md)

    def __map_cloud_folders_to_local(self, local_folders: list[str], cloud_root: str, cloud_folders: list[CloudFolderMetadata]) -> list[str]:
        cloud_dict = {folder.path_lower: folder.cloud_path for folder in cloud_folders} #dict

        local_folder_paths = [posixpath.join(cloud_root, folder) for folder in local_folders] #list
        local_folder_paths_filtered = filter(lambda name: not name.startswith('.'), local_folder_paths)
        local_dict = {path.lower(): path for path in local_folder_paths_filtered} #dict

        union_keys = set(cloud_dict.keys()).union(local_dict.keys())
        union_list = list(map(lambda key: cloud_dict[key] if key in cloud_dict else local_dict[key], union_keys))
        return union_list

    def download_files(self, cloud_files: list[CloudFileMetadata]):
        for cloud_file in cloud_files:
            cloud_path = cloud_file.cloud_path
            self._logger.info('downloading {} => {} ...'.format(cloud_path, self._localStore.get_absolute_path(cloud_path)))
            cloud_content, cloud_md = self._cloudStore.read(cloud_path)
            self._logger.debug('downloaded file: {}'.format(cloud_md))
            self._localStore.save(cloud_path, cloud_content, cloud_md.client_modified)

    def upload_files(self, local_files: list[LocalFileMetadata]):
        for local_file in local_files:
            cloud_path = local_file.cloud_path
            self._logger.info('uploading {} => {} ...'.format(local_file.local_path, cloud_path))
            content, local_md = self._localStore.read(cloud_path)
            self._cloudStore.save(cloud_path, content, local_md, overwrite=True)
