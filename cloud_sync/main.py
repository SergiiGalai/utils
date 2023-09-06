import src.logs.logger_colorer  #add log highlighting
import src.logs.logger as logger
import logging
from src.configs.config import StorageConfigProvider, StorageConfig
from src.command_handler import CommandHandler
from src.services.file_sync_service import FileSyncronizationService
from src.services.storage_strategy import StorageStrategyFactory
from src.stores.local.file_store import LocalFileStore
from src.clients.logger_ui import LoggerUi

log = logger.setupLogger(logging.DEBUG)

def create_configuration(logger: logging.Logger):
    configProvider = StorageConfigProvider(logger)
    arguments = configProvider.parse_arguments()
    return configProvider.get_config(arguments)

def create_command_handler(config: StorageConfig, logger: logging.Logger) -> CommandHandler:
    localStore = LocalFileStore(config, logger)
    strategy = StorageStrategyFactory(localStore, logger).create(config)
    fileService = FileSyncronizationService(strategy, localStore, config, logger)
    ui = LoggerUi(logger)
    return CommandHandler(fileService, ui, logger)

if __name__ == '__main__':
    conf = create_configuration(log)
    commandHandler = create_command_handler(conf, log)
    commandHandler.handle(conf.action, conf.cloud_dir)
