import posixpath
from logging import Logger
from src.configs.config import StorageConfig
from src.sync.file_sync_action_provider import FileSyncAction, FileSyncActionProvider
from src.sync.models import MapFilesResult
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.local.file_store import LocalFileStore
from src.sync.stores.local.path_provider import PathProvider
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, LocalFileMetadata


class FileSyncronizationService:
    def __init__(self,
                 local_store: LocalFileStore, cloud_store: CloudStore,
                 file_comparer: FileSyncActionProvider, path_provider: PathProvider,
                 config: StorageConfig, logger: Logger):
        self._recursive = config.recursive
        self._logger = logger
        self._path_provider = path_provider
        self._local_store = local_store
        self._cloud_store = cloud_store
        self._file_comparer = file_comparer
        self._logger.debug(config)

    @property
    def local_root(self) -> str:
        return self._path_provider.get_absolute_path()

    def map_files(self, cloud_path: str) -> MapFilesResult:
        self._logger.info('cloud_path={}'.format(cloud_path))

        local_result = self._local_store.list_folder(cloud_path)
        cloud_result = self._cloud_store.list_folder(cloud_path)

        result = self.__map_cloud_files_to_local(local_result.files, cloud_result.files)
        if self._recursive:
            cloud_folders = self.__map_cloud_folders_to_local(local_result.folders, cloud_path, cloud_result.folders)
            for cloud_folder in cloud_folders:
                result_sub = self.map_files(cloud_folder)
                result.extend(result_sub)
        else:
            self._logger.info('skipping subfolders because of configuration')
        return result

    def __map_cloud_files_to_local(self, local_files: list[LocalFileMetadata],
                                   cloud_files: list[CloudFileMetadata]) -> MapFilesResult:
        result = MapFilesResult()

        local_files_dict = {md.cloud_path.lower(): md for md in local_files}
        cloud_files_dict = {md.cloud_path.lower(): md for md in cloud_files}

        for key, cloud_md in cloud_files_dict.items():
            local_md = local_files_dict.get(key)
            if local_md is None:
                self._logger.info(
                    'file does NOT exist locally - {} => download list'.format(cloud_md.cloud_path))
                result.add_download(cloud_md)
            else:
                self._logger.debug('file exists locally - {}'.format(key))
                self.__add_to_list_by_file_comparison(
                    local_md, cloud_md, result)

        for key, local_md in local_files_dict.items():
            if not self.__exists_in_cloud(key, cloud_files_dict):
                self._logger.info(
                    'file does NOT exist in the cloud - {} => upload list'.format(local_md.local_path))
                result.add_upload(local_md)

        return result

    def __exists_in_cloud(self, file_key: str, files: dict[str, CloudFileMetadata]) -> bool:
        return file_key in files.keys()

    def __add_to_list_by_file_comparison(self, local_md: LocalFileMetadata,
                                         cloud_md: CloudFileMetadata, result: MapFilesResult):
        file_action = self._file_comparer.get_sync_action(local_md, cloud_md)
        match file_action:
            case FileSyncAction.UPLOAD:
                result.add_upload(local_md)
            case FileSyncAction.DOWNLOAD:
                result.add_download(cloud_md)

    def __map_cloud_folders_to_local(self, local_folders: list[str],
                                     cloud_root: str, cloud_folders: list[CloudFolderMetadata]) -> list[str]:
        cloud_dict = {folder.path_lower: folder.cloud_path for folder in cloud_folders}  # dict

        local_folder_paths = list(posixpath.join(cloud_root, folder) for folder in local_folders)
        local_folder_paths_filtered = filter(lambda name: not name.startswith('.'), local_folder_paths)
        local_dict = {path.lower(): path for path in local_folder_paths_filtered}  # dict

        union_keys = set(cloud_dict.keys()).union(local_dict.keys())
        union_list = list(map(lambda key: cloud_dict[key] if key in cloud_dict else local_dict[key], union_keys))
        return union_list

    def download_files(self, cloud_files: list[CloudFileMetadata]):
        for cloud_file in cloud_files:
            cloud_path = cloud_file.cloud_path
            self._logger.info('downloading {} => {} ...'.format(
                cloud_path, self._path_provider.get_absolute_path(cloud_path)))
            content, cloud_md = self._cloud_store.read(cloud_file.id)
            self._logger.debug('downloaded file: {}'.format(cloud_md))
            self._local_store.save(content, cloud_md)

    def upload_files(self, local_files: list[LocalFileMetadata]):
        for local_file in local_files:
            cloud_path = local_file.cloud_path
            self._logger.info('uploading {} => {} ...'.format(local_file.local_path, cloud_path))
            content, local_md = self._local_store.read(cloud_path)
            self._cloud_store.save(content, local_md, overwrite=True)
