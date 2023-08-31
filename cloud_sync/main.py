import src.logs.logger_colorer  #add log highlighting
import src.logs.logger as logger
import logging
from src.configs.config import StorageConfigProvider, StorageConfig
from src.command import CommandRunner
from src.services.file_sync_service import FileSyncronizationService
from src.services.storage_strategy import StorageStrategyFactory
from src.stores.local_file_store import LocalFileStore
from src.clients.ui import UI

log = logger.setupLogger(logging.DEBUG)

def create_configuration(logger: logging.Logger):
    configProvider = StorageConfigProvider(logger)
    arguments = configProvider.parse_arguments()
    return configProvider.get_config(arguments)

def create_command_runner(config: StorageConfig, logger: logging.Logger) -> CommandRunner:
    localStore = LocalFileStore(config, logger)
    strategy = StorageStrategyFactory(localStore, logger).create(config)
    fileService = FileSyncronizationService(strategy, localStore, config, logger)
    ui = UI(logger)
    return CommandRunner(localStore, fileService, ui, logger)

if __name__ == '__main__':
    conf = create_configuration(log)
    commandRunner = create_command_runner(conf, log)
    commandRunner.run(conf.action, conf.cloud_dir)
