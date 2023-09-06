import src.logs.logger_colorer  # add log highlighting
import src.logs.logger as logger
import logging
from src.configs.config import StorageConfigProvider, StorageConfig
from src.command_handler import CommandHandler
from src.services.file_sync_service import FileSyncronizationService
from src.services.storage_strategy import StorageStrategyFactory
from src.stores.local.dry_run_file_store import DryRunLocalFileStore
from src.clients.logger_ui import LoggerUi
from src.stores.local.path_provider import PathProvider

log = logger.setupLogger(logging.DEBUG)


def create_configuration(logger: logging.Logger):
    config_provider = StorageConfigProvider(logger)
    arguments = config_provider.parse_arguments()
    return config_provider.get_config(arguments)


def create_command_handler(config: StorageConfig, logger: logging.Logger) -> CommandHandler:
    path_provider = PathProvider(config, logger)
    local_store = DryRunLocalFileStore(config, path_provider, logger)
    strategy = StorageStrategyFactory(local_store, logger).create(config)
    sync_service = FileSyncronizationService(
        strategy, local_store, path_provider, config, logger)
    ui = LoggerUi(logger)
    return CommandHandler(sync_service, ui, logger)


if __name__ == '__main__':
    conf = create_configuration(log)
    commandHandler = create_command_handler(conf, log)
    commandHandler.handle(conf.action, conf.cloud_dir)
