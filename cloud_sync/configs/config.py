import sys
import os
from configparser import ConfigParser
from argparse import ArgumentParser
from logging import Logger
from dataclasses import dataclass

@dataclass
class Config:
   action: str
   token: str
   local_dir: str
   cloud_dir: str
   dry_run: bool
   recursive: bool

class ConfigProvider:
   def __init__(self, logger: Logger):
      self.logger = logger

   def parse_arguments(self) -> ArgumentParser:
      self.logger.debug('parse_arguments started')
      parser = ArgumentParser()
      parser.add_argument('-c', '--config', help='Config file')
      parser.add_argument('--storage', help='dropbox|gdrive')
      parser.add_argument('--action', help='download|upload|sync files (sync if not exist)')
      parser.add_argument('--token', help='Access token')
      parser.add_argument('--local_dir', help='Local directory to upload')
      parser.add_argument('--cloud_dir', help='Destination folder on your cloud storage')
      parser.add_argument('--yes', '-y', action='store_true', help='Answer yes to all questions')
      parser.add_argument('--no', '-n', action='store_true', help='Answer no to all questions')
      parser.add_argument('--default', '-d', action='store_true', help='Take default answer on all questions')
      parser.add_argument('--dryrun', help='Do not change files if True')
      parser.add_argument('--recursive', help='Process subfolders if True')
      return parser.parse_args()

   def __get_config_file_locations(self, path: str):
      if path:
         return [path]
      else:
         return [
               'config.ini',
               '/etc/cloud_sync/config.ini',
               os.path.join(os.path.expanduser('~'), '.cloud_sync_config.ini')
         ]

   def __validate_booleans(self, args):
      if sum([bool(b) for b in (args.yes, args.no, args.default)]) > 1:
         self.logger.error('At most one of --yes, --no, --default is allowed')
         sys.exit(2)

   def __get_from_args_or_config(self, args, config):
      self.logger.debug('__get_from_args_or_config started. args={}, config={}'.format(args, config))
      action = args.action or config.get('ACTION')
      token = args.token or config.get('TOKEN')
      local_dir = args.local_dir or config.get('LOCAL_DIR')
      cloud_dir = args.cloud_dir or config.get('CLOUD_DIR')
      dry_run = args.dryrun or (args.dryrun is None and config.getboolean('DRY_RUN'))
      recursive = args.recursive or (args.recursive is None and config.getboolean('RECURSIVE'))

      self.__validate_booleans(args)
      if local_dir is not None and local_dir.startswith('.'):
         local_dir = os.path.abspath(local_dir)

      return Config(action, token, local_dir, cloud_dir, dry_run, recursive)

   def __get_storage_name(self, args, config):
      if not config.has_section('GENERAL'): config['GENERAL'] = {}
      storage = args.storage or config['GENERAL'].get('STORAGE')
      match storage:
         case 'GDRIVE' | 'gdrive': return 'GDRIVE'
         case 'DROPBOX' | 'dropbox': return 'DROPBOX'
         case _: return 'DROPBOX'

   def __get_config_file(self, locations):
      config = ConfigParser()
      config.read(locations)
      return config

   def __get_storage_config(self, storageName, args, configFile):
      if not configFile.has_section(storageName): configFile[storageName] = {}
      storageConfig = configFile[storageName]
      return self.__get_from_args_or_config(args, storageConfig)

   def __merge_configs(self, default: Config, override: Config):
      return Config(
         override.action or default.action,
         override.token or default.token,
         override.local_dir or default.local_dir,
         override.cloud_dir or default.cloud_dir,
         override.dry_run or (override.dry_run is None and default.dry_run),
         override.recursive or (override.recursive is None and default.recursive),
      )

   def get_config(self, args):
      self.logger.debug('get_config started, args={}')

      configLocations = self.__get_config_file_locations(args.config)
      defaultConfigFile = self.__get_config_file(configLocations)
      defaultFileStorageName = self.__get_storage_name(args, defaultConfigFile)
      defaultConfig = self.__get_storage_config(defaultFileStorageName, args, defaultConfigFile)

      overrideLocations = [location + '.secret.ini' for location in configLocations]
      overrideConfigFile = self.__get_config_file(overrideLocations)
      overrideConfig = self.__get_storage_config(defaultFileStorageName, args, overrideConfigFile)

      resultConfig = self.__merge_configs(defaultConfig, overrideConfig)
      return resultConfig
