import sys
import os
from configparser import ConfigParser, SectionProxy
from argparse import ArgumentParser, Namespace
from logging import Logger
from dataclasses import dataclass


@dataclass
class StorageConfig:
    storage_name: str
    action: str
    token: str
    local_dir: str
    cloud_dir: str
    dry_run: bool
    recursive: bool


class StorageConfigProvider:
    def __init__(self, logger: Logger):
        self._logger = logger

    def parse_arguments(self) -> Namespace:
        self._logger.debug('parse_arguments started')
        parser = ArgumentParser()
        parser.add_argument('-c', '--config', help='Config file')
        parser.add_argument('--storage', help='dropbox|gdrive')
        parser.add_argument('--action', help='download|upload|sync files (sync if not exist)')
        parser.add_argument('--token', help='Access token')
        parser.add_argument('--local_dir', help='Local directory to upload')
        parser.add_argument('--cloud_dir', help='Destination folder on your cloud storage')
        parser.add_argument('--yes', '-y', action='store_true', help='Answer yes to all questions')
        parser.add_argument('--no', '-n', action='store_true', help='Answer no to all questions')
        parser.add_argument('--default', '-d', action='store_true',
                            help='Take default answer on all questions')
        parser.add_argument('--dryrun', help='Do not change files if True')
        parser.add_argument('--recursive', help='Process subfolders if True')
        namespace = parser.parse_args()
        self.__validate_args_defaults(namespace)
        return namespace

    def get_config(self, args: Namespace):
        self._logger.debug('args={}')
        configFilePaths = self.__get_config_file_locations(args.config)

        defaultConfigParser = self.__get_config_parser(configFilePaths)
        activeStorageName = self.__get_active_storage_name(args, defaultConfigParser)
        defaultConfig = self.__get_storage_config(activeStorageName, args, defaultConfigParser)

        overrideFilePaths = [location + '.secret.ini'
                             for location in configFilePaths]
        overrideConfigParser = self.__get_config_parser(overrideFilePaths)
        overrideConfig = self.__get_storage_config(
            activeStorageName, args, overrideConfigParser)

        resultConfig = self.__merge_configs(defaultConfig, overrideConfig)
        return resultConfig

    def __get_config_file_locations(self, path: str):
        if path:
            return [path]
        else:
            return [
                'config.ini',
                '/etc/cloud_sync/config.ini',
                os.path.join(os.path.expanduser('~'),
                             '.cloud_sync_config.ini')
            ]

    def __get_config_parser(self, filePaths):
        config = ConfigParser()
        config.read(filePaths)
        return config

    def __get_active_storage_name(self, args: Namespace, config: ConfigParser):
        if not config.has_section('GENERAL'):
            config['GENERAL'] = {}
        storage = args.storage or config['GENERAL'].get('STORAGE')
        match storage:
            case 'GDRIVE' | 'gdrive': return 'GDRIVE'
            case 'DROPBOX' | 'dropbox': return 'DROPBOX'
            case _: return 'DROPBOX'

    def __get_storage_config(self, storageName: str, args: Namespace, configParser: ConfigParser) -> StorageConfig:
        if not configParser.has_section(storageName):
            configParser[storageName] = {}
        storageConfig = configParser[storageName]
        config = self.__get_config_from_args_or_file(
            storageName, args, storageConfig)
        return config

    def __get_config_from_args_or_file(self, storageName: str, args: Namespace, config: SectionProxy) -> StorageConfig:
        self._logger.debug('storageName={}, config={}, args={}'.format(storageName, config, args))

        action = args.action or config.get('ACTION')
        token = args.token or config.get('TOKEN')
        local_dir = args.local_dir or config.get('LOCAL_DIR')
        cloud_dir = args.cloud_dir or config.get('CLOUD_DIR')
        dry_run = args.dryrun or (args.dryrun is None and config.getboolean('DRY_RUN'))
        recursive = args.recursive or (args.recursive is None and config.getboolean('RECURSIVE'))

        if local_dir is not None and local_dir.startswith('.'):
            local_dir = os.path.abspath(local_dir)

        return StorageConfig(storageName, action, token, local_dir, cloud_dir, dry_run, recursive)

    def __validate_args_defaults(self, args: Namespace):
        if sum([bool(b) for b in (args.yes, args.no, args.default)]) > 1:
            self._logger.error('At most one of --yes, --no, --default is allowed')
            sys.exit(2)

    def __merge_configs(self, default: StorageConfig, override: StorageConfig):
        return StorageConfig(
            override.storage_name or default.storage_name,
            override.action or default.action,
            override.token or default.token,
            override.local_dir or default.local_dir,
            override.cloud_dir or default.cloud_dir,
            override.dry_run or (override.dry_run is None and default.dry_run),
            override.recursive or (override.recursive is None and default.recursive),
        )
