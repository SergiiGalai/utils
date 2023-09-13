from logging import Logger
from src.sync.models import FileSyncAction, FileComparison
from src.sync.comparison.file_content_comparer import FileContentComparer
from src.sync.comparison.file_metadata_comparer import FileMetadataComparer
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class FileSyncActionProvider:
    def __init__(self, content_comparer: FileContentComparer, logger: Logger):
        self._metadata_comparer = FileMetadataComparer(logger)
        self._content_comparer = content_comparer
        self._logger = logger

    def get_sync_action(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> FileSyncAction:
        need_time_verification, comparisonResult = self.__are_equal(local_md, cloud_md)
        if need_time_verification:
            if local_md.client_modified > cloud_md.client_modified:
                self._logger.info('file {} has changed since last sync (cloud={} < local={}) => upload list'
                                  .format(local_md.full_path, cloud_md.client_modified, local_md.client_modified))
                return FileSyncAction.UPLOAD
            self._logger.info('file {} has changed since last sync (cloud={} > local={}) => download list'
                              .format(cloud_md.cloud_path, cloud_md.client_modified, local_md.client_modified))
            return FileSyncAction.DOWNLOAD
        if comparisonResult == FileComparison.ERROR:
            return FileSyncAction.CONFLICT
        return FileSyncAction.SKIP

    def __are_equal(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> tuple[bool, FileComparison]:
        cloud_path = cloud_md.cloud_path
        comparison_by_md = self._metadata_comparer.are_equal(local_md, cloud_md)
        match comparison_by_md:
            case FileComparison.EQUAL:
                self._logger.info('file {} already the same [by metadata]. Skip'.format(cloud_path))
                return False, FileComparison.EQUAL
            case FileComparison.DIF_BY_SIZE:
                return True, FileComparison.DIF_BY_SIZE
            case FileComparison.DIF_BY_DATE:
                self._logger.info('file {} exists with different stats. Comparing files by content'.format(cloud_path))
                if self._content_comparer.are_equal(local_md, cloud_md):
                    self._logger.info('file {} already the same [by content]. Skip'.format(cloud_path))
                    return False, FileComparison.EQUAL
                self._logger.info('Local and cloud file {} is different'.format(cloud_path))
                return True, FileComparison.DIF_BY_DATE
            case _:
                self._logger.info('Cannot compare local file {} and cloud file {}. Skip'.format(
                    cloud_path, local_md.cloud_path))
                return False, FileComparison.ERROR
