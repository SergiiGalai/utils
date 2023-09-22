
import datetime
from src.sync.stores.models import CloudFileMetadata, LocalFileMetadata


def create_local_file(modified_day=1, size=2000,
                      cloud_path='/Target/File1.pdf',
                      local_path='C:\\Path\\CloudRoot\\target\\File1.pdf',
                      name='File1.pdf'):
    return LocalFileMetadata(
        name, cloud_path,
        __get_modified_date(modified_day),
        size, local_path,
        'application/unknown')


def create_cloud_file(modified_day=1, size=2000,
                      cloud_path='/Target/File1.pdf',
                      name='File1.pdf',
                      id='idtargetf1',
                      hash='123'):
    return CloudFileMetadata(
        name, cloud_path,
        __get_modified_date(modified_day),
        size, id, hash)


def __get_modified_date(day=1):
    return datetime.datetime(2023, 8, day, 20, 14, 14)
