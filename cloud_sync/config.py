import argparse
import sys
import os
import configparser
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

   def __get_config_file_location(self, path: str):
      if path:
         return path
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

   def __parse_arguments(self):
      self.logger.debug('parse_arguments started')
      parser = argparse.ArgumentParser()
      parser.add_argument('-c', '--config', help='Config file')
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

   def __get_from_args_or_config(self, args, config):
      self.logger.debug('__get_from_args_or_config started. args={}, config={}'.format(args, config))
      action = args.action or config.get('ACTION')
      token = args.token or config.get('TOKEN')
      local_dir = args.local_dir or config.get('LOCAL_DIR') or ""
      cloud_dir = args.cloud_dir or config.get('CLOUD_DIR') or ""
      dry_run = args.dryrun or config.getboolean('DRY_RUN')
      recursive = args.recursive or config.getboolean('RECURSIVE')

      self.__validate_booleans(args)
      if local_dir.startswith('.'):
         local_dir = os.path.abspath(local_dir)

      return Config(action, token, local_dir, cloud_dir, dry_run, recursive)

   def get_config(self):
      self.logger.debug('get_config started')

      args = self.__parse_arguments()
      config_location = self.__get_config_file_location( args.config )
      config = configparser.ConfigParser()
      config.read( config_location )

      if not config.has_section('GENERAL'): config['GENERAL'] = {}

      match config['GENERAL'].get('STORAGE'):
         case 'GDRIVE': storage = 'GDRIVE'
         case 'DROPBOX': storage = 'DROPBOX'
         case _:
               print('Not supported STORAGE value')
               sys.exit(2)

      if not config.has_section(storage): config[storage] = {}
      storageConfig = config[storage]

      return self.__get_from_args_or_config(args, storageConfig)
