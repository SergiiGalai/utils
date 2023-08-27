from posixpath import join as urljoin
from logging import Logger
from src.configs.config import StorageConfig
from src.stores.cloud_store import CloudStore
from src.stores.local_file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, CloudFolderMetadata, LocalFileMetadata

class FileSyncronizationService:
    def __init__(self, localStore: LocalFileStore, cloudStore: CloudStore, config: StorageConfig, logger: Logger):
        self._localStore = localStore
        self._cloudStore = cloudStore
        self._recursive = config.recursive
        self._logger = logger
        self._logger.debug(config)

    def map_files(self, cloud_path: str):
        self._logger.info('cloud_path={}'.format(cloud_path))

        local_dirs, local_file_mds = self._localStore.list_folder(cloud_path)
        cloud_dirs, cloud_files = self._cloudStore.list_folder(cloud_path)

        download_files, upload_files = self.__map_cloud_files_to_local(local_file_mds, cloud_path, cloud_files)
        if self._recursive:
            process_cloud_folders = self.__map_cloud_folders_to_local(local_dirs, cloud_path, cloud_dirs)
            for cloud_folder in process_cloud_folders:
                download_sub, upload_sub = self.map_files(cloud_folder)
                download_files.extend(download_sub)
                upload_files.extend(upload_sub)
        else:
            self._logger.info('skipping subfolders because of configuration')
        return download_files, upload_files

    def __map_cloud_files_to_local(self, local_file_mds: dict[str, LocalFileMetadata], cloud_path: str, cloud_files: list[CloudFileMetadata]):
        upload_list = list[str]()
        download_list = list[str]()

        for cloud_md in cloud_files:
            name = cloud_md.name
            local_md = local_file_mds.get(name)
            if local_md is None:
                self._logger.info('file NOT found locally - {} => download list'.format(cloud_md.path_display))
                download_list.append(cloud_md.path_display)
            else:
                self._logger.debug('file found locally - {}'.format(name))
                self._add_to_list_by_file_comparison(local_md, cloud_md, upload_list, download_list)

        cloud_file_names = {f.name for f in cloud_files} #set
        for file_name in local_file_mds:
            if file_name in cloud_file_names:
                continue
            file = local_file_mds[file_name]
            self._logger.info('file NOT found on dropbox - {} => upload list'.format(file.path))
            cloud_file_path = urljoin(cloud_path, file_name)
            upload_list.append(cloud_file_path)

        return download_list, upload_list

    def _add_to_list_by_file_comparison(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata, upload_list: list[str], download_list: list[str]):
        cloud_path = cloud_md.path_display
        if self.__are_equal_by_metadata(local_md, cloud_md):
            self._logger.info('file {} already synced [by metadata]. Skip'.format(cloud_path))
        else:
            self._logger.info('file {} exists with different stats. Downloading temporary'.format(cloud_path))
            if self.__are_equal_by_content(local_md.path, cloud_path):
                self._logger.info('file {} already synced [by content]. Skip'.format(cloud_path))
            else:
                if local_md.client_modified > cloud_md.client_modified:
                    self._logger.info('file {} has changed since last sync (cloud={} < local={}) => upload list'
                        .format(local_md.path, cloud_md.client_modified, local_md.client_modified))
                    upload_list.append(cloud_path)
                else:
                    self._logger.info('file {} has changed since last sync (cloud={} > local={}) => download list'
                        .format(cloud_path, cloud_md.client_modified, local_md.client_modified))
                    download_list.append(cloud_path)

    def __map_cloud_folders_to_local(self, local_folders: list[str], cloud_root: str, cloud_folders: list[CloudFolderMetadata]):
        cloud_dict = {folder.path_lower: folder.path_display for folder in cloud_folders}

        local_folder_paths = [urljoin(cloud_root, folder) for folder in local_folders]
        local_folder_paths_filtered = filter(lambda name: not name.startswith('.'), local_folder_paths)
        local_dict = {path.lower(): path for path in local_folder_paths_filtered}

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
        local_content, _ = self._localStore.read(local_path)
        cloud_content, _ = self._cloudStore.read(cloud_path)
        return cloud_content == local_content
