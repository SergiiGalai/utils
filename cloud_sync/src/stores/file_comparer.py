from abc import abstractmethod
from logging import Logger
from src.services.models import FileAction, FileComparison
from src.stores.cloud_store import CloudStore
from src.stores.local.file_store import LocalFileStore
from src.stores.models import CloudFileMetadata, LocalFileMetadata


class FileComparer:
    def __init__(self, local_store: LocalFileStore, cloud_store: CloudStore, logger: Logger):
        self._local_store = local_store
        self._cloud_store = cloud_store
        self._logger = logger

    def get_file_action(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> FileAction:
        need_time_verification, comparisonResult = self.__are_equal(local_md, cloud_md)
        if need_time_verification:
            if local_md.client_modified > cloud_md.client_modified:
                self._logger.info('file {} has changed since last sync (cloud={} < local={}) => upload list'
                                  .format(local_md.local_path, cloud_md.client_modified, local_md.client_modified))
                return FileAction.UPLOAD
            self._logger.info('file {} has changed since last sync (cloud={} > local={}) => download list'
                              .format(cloud_md.cloud_path, cloud_md.client_modified, local_md.client_modified))
            return FileAction.DOWNLOAD
        if comparisonResult == FileComparison.ERROR:
            return FileAction.CONFLICT
        return FileAction.SKIP

    def __are_equal(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> tuple[bool, FileComparison]:
        cloud_path = cloud_md.cloud_path
        comparison_by_md = self.__are_equal_by_metadata(local_md, cloud_md)
        match comparison_by_md:
            case FileComparison.EQUAL:
                self._logger.info(
                    'file {} already the same [by metadata]. Skip'.format(cloud_path))
                return False, FileComparison.EQUAL
            case FileComparison.DIF_BY_SIZE:
                return True, FileComparison.DIF_BY_SIZE
            case FileComparison.DIF_BY_DATE:
                self._logger.info('file {} exists with different stats. Comparing files by content'.
                                  format(cloud_path))
                if self._are_equal_by_content(local_md, cloud_md):
                    self._logger.info('file {} already the same [by content]. Skip'.
                                      format(cloud_path))
                    return False, FileComparison.EQUAL
                self._logger.info('Local and cloud file {} is different'.format(cloud_path))
                return True, FileComparison.DIF_BY_DATE
            case _:
                self._logger.info('Cannot compare local file {} and cloud file {}. Skip'.format(
                    cloud_path, local_md.cloud_path))
                return False, FileComparison.ERROR

    def __are_equal_by_metadata(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> FileComparison:
        if local_md.name != cloud_md.name:
            self._logger.info('file diff by name: local={}, remote={}'.format(local_md.name, cloud_md.name))
            return FileComparison.DIF_BY_NAME

        if local_md.client_modified != cloud_md.client_modified and local_md.size != cloud_md.size:
            self._logger.info('file={} diff by size: local={}, remote={}'.format(
                local_md.name, local_md.size, cloud_md.size))
            return FileComparison.DIF_BY_SIZE

        if local_md.client_modified != cloud_md.client_modified:
            self._logger.info('file={} diff by date: local={}, remote={}'.format(
                local_md.name, local_md.client_modified, cloud_md.client_modified))
            return FileComparison.DIF_BY_DATE

        if local_md.size != cloud_md.size:
            self._logger.info('file={} diff by size: local={}, remote={}'.format(
                local_md.name, local_md.size, cloud_md.size))
            return FileComparison.ERROR

        return FileComparison.EQUAL

    @abstractmethod
    def _are_equal_by_content(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> bool:
         raise NotImplementedError
