
import datetime
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, CloudId, LocalFileMetadata, LocalFolderMetadata


def create_local_file(cloud_path='/Target/File1.pdf',
                      local_path='d:\\sync\\CloudRoot\\target\\File1.pdf',
                      name='File1.pdf',
                      modified_day=1, size=2000,):
    return LocalFileMetadata(name, cloud_path,
                             __get_modified_date(modified_day),
                             size, local_path,
                             'application/unknown')


def create_cloud_file(cloud_path='/Target/File1.pdf',
                      name='File1.pdf',
                      id='idtargetf1',
                      folder=CloudId('TargetId', '/Target'),
                      hash='123',
                      modified_day=1, size=2000,):
    return CloudFileMetadata(name, cloud_path,
                             __get_modified_date(modified_day),
                             size, id,
                             folder, hash)


def create_cloud_folder(cloud_path='/Target',
                        lower_path='/target',
                        name='Target',
                        id='idTargetDir'):
    return CloudFolderMetadata(id, name, lower_path, cloud_path)


def create_local_folder(cloud_path='/Target',
                        full_path='d:\\sync\\CloudRoot\\Target',
                        name='Target'):
    return LocalFolderMetadata(name, cloud_path, full_path)


def __get_modified_date(day=1):
    return datetime.datetime(2023, 8, day, 20, 14, 14)
