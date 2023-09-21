from logging import Logger
from src.sync.models import FileComparison
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class FileMetadataComparer:
    def __init__(self, logger: Logger):
        self._logger = logger

    def are_equal(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> FileComparison:
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

