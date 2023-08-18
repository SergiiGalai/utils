import src.logs.logger_colorer  #add log highlighting
import src.logs.logger as logger
import logging
from src.configs.config import ConfigProvider, Config
from src.command import CommandRunner
from src.services.file_sync_service import FileSyncronizationService
from src.stores.local_file_store import LocalFileStore
from src.stores.dropbox_store import DropboxStore
from src.stores.gdrive_store import GdriveStore
from src.clients.ui import UI

log = logger.setupLogger(logging.DEBUG)

def create_configuration(logger: logging.Logger):
    configProvider = ConfigProvider(logger)
    arguments = configProvider.parse_arguments()
    return configProvider.get_config(arguments)

def create_command_runner(config: Config, logger: logging.Logger) -> CommandRunner:
    localStore = LocalFileStore(config, logger)
    dboxStore = DropboxStore(config, logger)
    gdriveStore = GdriveStore(config, logger)
    fileService = FileSyncronizationService(localStore, dboxStore, gdriveStore, config, logger)
    ui = UI(logger)
    return CommandRunner(localStore, dboxStore, fileService, ui, logger)

if __name__ == '__main__':
    conf = create_configuration(log)
    commandRunner = create_command_runner(conf, log)
    commandRunner.run(conf.action, conf.cloud_dir)
