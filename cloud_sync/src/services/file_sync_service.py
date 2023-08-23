import pathlib
from posixpath import join as urljoin
from logging import Logger
from src.configs.config import StorageConfig
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore, LocalFileMetadata
from src.stores.models import CloudFileMetadata

class FileSyncronizationService:
    def __init__(self, localStore: LocalFileStore, cloudStore: CloudStore, config: StorageConfig, logger: Logger):
        self._localStore = localStore
        self._cloudStore = cloudStore
        self._recursive = config.recursive
        self._logger = logger
        self._logger.debug(config)

    def __list_from_cloud(self, cloud_path):
        cloud_root, cloud_dirs, cloud_files = self._cloudStore.list_folder(cloud_path)
        self._logger.debug('files={}'.format(cloud_files))
        self._logger.debug('folders={}'.format(cloud_dirs))
        return cloud_root, cloud_dirs, cloud_files

    def map_recursive(self, cloud_path: str):
        self._logger.info('cloud_path={}'.format(cloud_path))

        local_root, local_dirs, local_files = self._localStore.list_folder(cloud_path)
        cloud_root, cloud_dirs, cloud_files = self.__list_from_cloud(cloud_path)
        return None, None

        download_files, upload_files = self.__map_cloud_files_to_local(local_root, local_files, cloud_root, cloud_files)
        if self._recursive:
            process_cloud_folders = self.__map_cloud_folders_to_local(local_dirs, cloud_root, cloud_dirs)
            for cloud_folder in process_cloud_folders:
                download_sub, upload_sub = self.map_recursive(cloud_folder)
                download_files.extend(download_sub)
                upload_files.extend(upload_sub)
        else:
            self._logger.info('skipping subfolders because of configuration')
        return download_files, upload_files

    def __map_cloud_files_to_local(self, local_root: str, local_files: list, cloud_root: str, cloud_filemetadatas: list):
        upload_list = list()
        download_list = list()

        for cloud_file_md in cloud_filemetadatas:
            name = cloud_file_md.name
            cloud_path = cloud_file_md.path_display
            local_path = self._localStore.get_absolute_path(cloud_path)

            if name in local_files:
                self._logger.debug('file found locally - {}'.format(name))
                local_md = self._localStore.get_file_metadata(local_path)
                if self.__are_equal_by_metadata(local_md, cloud_file_md):
                    self._logger.info('file {} already synced [by metadata]. Skip'.format(cloud_path))
                else:
                    self._logger.info('file {} exists with different stats. Downloading temporary'.format(cloud_path))
                    if self.__are_equal_by_content(local_path, cloud_path):
                        self._logger.info('file {} already synced [by content]. Skip'.format(cloud_path))
                    else:
                        if local_md.client_modified > cloud_file_md.client_modified:
                            self._logger.info('file {} has changed since last sync (cloud={} < local={}) => upload list'
                                .format(local_path, cloud_file_md.client_modified, local_md.client_modified))
                            upload_list.append(cloud_path)
                        else:
                            self._logger.info('file {} has changed since last sync (cloud={} > local={}) => download list'
                                .format(cloud_path, cloud_file_md.client_modified, local_md.client_modified))
                            download_list.append(cloud_path)
            else:
                self._logger.info('file NOT found locally - {} => download list'.format(cloud_path))
                download_list.append(cloud_path)

        cloud_names = list(map(lambda f: f.name, cloud_filemetadatas))
        local_only = filter(lambda name: name not in cloud_names, local_files)
        for name in local_only:
            local_path = pathlib.PurePath(local_root).joinpath(name)
            self._logger.info('file NOT found on dropbox - {} => upload list'.format(local_path))
            cloud_path = urljoin(cloud_root, name)
            upload_list.append(cloud_path)

        return download_list, upload_list

    def __map_cloud_folders_to_local(self, local_folders: list, cloud_root: str, cloud_folders: list):
        cloud_dict = dict(map(lambda f: (f.path_lower, f.path_display), cloud_folders))

        local_folder_paths = map(lambda name: urljoin(cloud_root, name), local_folders)
        local_folder_paths_filtered = filter(lambda name: not name.startswith('.'), local_folder_paths)
        local_dict = {v.lower(): v for v in local_folder_paths_filtered}

        union_keys = set(cloud_dict.keys()).union(local_dict.keys())
        union_list = list(map(lambda key: cloud_dict[key] if key in cloud_dict else local_dict[key], union_keys))
        return union_list

    def __are_equal_by_metadata(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata):
        equal_by_name = (local_md.name == cloud_md.name)
        equal_by_size = (local_md.size == cloud_md.size)
        equal_by_date = (local_md.client_modified == cloud_md.client_modified)
        if not equal_by_name:
            self._logger.info('file diff by name: local={}, remote={}'.format(local_md.name, cloud_md.name))
            return False
        if not equal_by_size:
            self._logger.info('file={} diff by size: local={}, remote={}'.format(local_md.name, local_md.size, cloud_md.size))
            return False
        if not equal_by_date:
            self._logger.info('file={} diff by date: local={}, remote={}'.format(local_md.name, local_md.client_modified, cloud_md.client_modified))
            return False
        return True

    def __are_equal_by_content(self, local_path: str, cloud_path: str):
        content_local, local_md = self._localStore.read(local_path)
        response, cloud_md = self._cloudStore.read(cloud_path)
        return response.content == content_local
