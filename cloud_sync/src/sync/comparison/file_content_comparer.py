from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


class FileContentComparer:
    def are_equal(self, local_md: LocalFileMetadata, cloud_md: CloudFileMetadata) -> bool:
        raise NotImplementedError
