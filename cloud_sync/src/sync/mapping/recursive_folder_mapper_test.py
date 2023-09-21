import datetime
import unittest
from unittest.mock import Mock
import logging
from src.configs.config import StorageConfig
from src.sync.mapping.file_mapper import FileMapper
from src.sync.mapping.recursive_folder_mapper import RecursiveFolderMapper
from src.sync.mapping.subfolder_mapper import SubfolderMapper
from src.sync.models import MapFolderResult
from src.sync.stores.cloud_store import CloudStore
from src.sync.stores.local.local_file_store import LocalFileStore
from src.sync.stores.models import CloudFileMetadata, CloudFolderMetadata, ListCloudFolderResult, ListLocalFolderResult, LocalFileMetadata, LocalFolderMetadata


class RecursiveFolderMapperTests(unittest.TestCase):

    def setUp(self):
        logger = Mock(logging.Logger)
        self._local_store = Mock(LocalFileStore)
        self._cloud_store = Mock(CloudStore)
        self._file_mapper = Mock(FileMapper)
        self._subfolder_mapper = Mock(SubfolderMapper)
        self._config = Mock(StorageConfig)
        self._config.recursive = True
        self._sut = RecursiveFolderMapper(self._local_store, self._cloud_store,
                                         self._file_mapper, self._subfolder_mapper,
                                         self._config, logger)

    def test_files_from_mapper_When_recursively_list_target_folder_but_without_subfolders(self):
        # arrange
        cloud_files_target, _ = self.__create_target_cloud_folder()
        self.__mock_local_store()
        self._cloud_store.list_folder.return_value = ListCloudFolderResult(cloud_files_target)
        self._file_mapper.map_cloud_to_local.return_value = MapFolderResult(cloud_files_target)
        # act
        actual = self._sut.map_folder('/Target')
        # assert
        self.assertEqual(actual.download, cloud_files_target)
        self.assertEqual(actual.upload, [])

    def test_files_from_mapper_When_non_resursively_list_target_folder_with_subfolders(self):
        # arrange
        self._config.recursive = False
        cloud_files_target, cloud_folders_target = self.__create_target_cloud_folder()
        self.__mock_local_store()
        self._cloud_store.list_folder.return_value = ListCloudFolderResult(cloud_files_target, cloud_folders_target)
        self._file_mapper.map_cloud_to_local.return_value = MapFolderResult(cloud_files_target)
        # act
        actual = self._sut.map_folder('/Target')
        # assert
        self.assertEqual(actual.download, cloud_files_target)
        self.assertEqual(actual.upload, [])

    def test_files_and_subfolders_from_mapper_When_recursively_list_target_folder(self):
        # arrange
        cloud_files_target, cloud_folders_target = self.__create_target_cloud_folder()
        cloud_file_sub1 = self.__create_cloud_file('/Target/Sub1/File1.pdf', 'File1.pdf', 'idsubf1')
        cloud_file_sub2 = self.__create_cloud_file('/Target/Sub2/File2.pdf', 'File2.pdf', 'idsubf2')
        self.__mock_local_store()
        self._cloud_store.list_folder.side_effect = [ListCloudFolderResult(cloud_files_target, cloud_folders_target),
                                                     ListCloudFolderResult([cloud_file_sub1]),
                                                     ListCloudFolderResult([cloud_file_sub2])]
        self._file_mapper.map_cloud_to_local.side_effect = [MapFolderResult(cloud_files_target.copy()),
                                                            MapFolderResult([cloud_file_sub1]),
                                                            MapFolderResult([cloud_file_sub2])]
        self._subfolder_mapper.map_cloud_to_local.side_effect = [set(['Sub1', 'Sub2']),
                                                                 set()]
        # act
        actual = self._sut.map_folder('/Target')
        # assert
        self.assertEqual(actual.download, cloud_files_target + [cloud_file_sub1, cloud_file_sub2])

    def __create_target_cloud_folder(self):
        file = self.__create_cloud_file('/Target/File1.pdf', 'File1.pdf', id='idf1')
        folder_sub1 = CloudFolderMetadata('idsubd1', 'Sub1', '/target/sub1', '/Target/Sub1')
        folder_sub2 = CloudFolderMetadata('idsubd2', 'Sub2', '/target/sub2', '/Target/Sub2')
        return [file], [folder_sub1, folder_sub2]

    @staticmethod
    def __create_cloud_file(cloud_path, name, id):
        return CloudFileMetadata(name, cloud_path,
                                 datetime.datetime(2023, 8, 15, 14, 27, 44),
                                 12345, id, '0')

    def __mock_local_store(self):
        self._local_store.list_folder.return_value = ListLocalFolderResult([], [])
