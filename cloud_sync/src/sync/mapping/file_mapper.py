from logging import Logger
from src.sync.file_sync_action_provider import FileSyncAction, FileSyncActionProvider
from src.sync.models import MapFolderResult
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class FileMapper:
    def __init__(self,
                 file_sync_action_provider: FileSyncActionProvider,
                 logger: Logger):
        self._logger = logger
        self._file_sync_action_provider = file_sync_action_provider

    def map_cloud_to_local(self,
                           cloud_list: list[CloudFileMetadata],
                           local_list: list[LocalFileMetadata]) -> MapFolderResult:
        result = MapFolderResult()
        local_dict = self.__to_local_dict(local_list)
        cloud_dict = self.__to_cloud_dict(cloud_list)
        for key, cloud_file in cloud_dict.items():
            local_file = local_dict.get(key)
            if local_file is None:
                self.__add_to_download(cloud_file, result)
            else:
                self.__add_by_comparison(local_file, cloud_file, result)
        for key, local_file in local_dict.items():
            if key not in cloud_dict:
                self.__add_to_upload(local_file, result)
        return result

    def __to_local_dict(self, files: list[LocalFileMetadata]) -> dict[str, LocalFileMetadata]:
        return {md.cloud_path.lower(): md for md in files}

    def __to_cloud_dict(self, files: list[CloudFileMetadata]) -> dict[str, CloudFileMetadata]:
        return {md.cloud_path.lower(): md for md in files}

    def __add_to_download(self, cloud_md: CloudFileMetadata, result: MapFolderResult):
        self._logger.info('file does NOT exist locally - {} => download list'.format(cloud_md.cloud_path))
        result.add_download(cloud_md)

    def __add_to_upload(self, local_md: LocalFileMetadata, result: MapFolderResult):
        self._logger.info('file does NOT exist in the cloud - {} => upload list'.format(local_md.local_path))
        result.add_upload(local_md)

    def __add_by_comparison(self,
                            local_md: LocalFileMetadata,
                            cloud_md: CloudFileMetadata,
                            result: MapFolderResult):
        self._logger.debug('file exists locally - {}'.format(local_md.cloud_path))
        file_action = self._file_sync_action_provider.get_sync_action(local_md, cloud_md)
        match file_action:
            case FileSyncAction.UPLOAD:
                result.add_upload(local_md)
            case FileSyncAction.DOWNLOAD:
                result.add_download(cloud_md)
