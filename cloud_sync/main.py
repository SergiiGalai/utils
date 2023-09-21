import src.logs.logger_colorer  # add log highlighting
import src.logs.logger as logger
import logging
from src.clients.console_ui import ConsoleUi
from src.clients.command_ui import CommandHandlerUi
from src.configs.config import StorageConfigProvider, StorageConfig
from src.command_handler import CommandHandler
from src.sync.file_sync_service import FileSyncronizationService
from src.sync.mapping.file_mapper import FileMapper
from src.sync.mapping.recursive_folder_mapper import RecursiveFolderMapper
from src.sync.mapping.subfolder_mapper import SubfolderMapper
from src.sync.storage_strategy import StorageStrategyFactory
from src.sync.file_sync_action_provider import FileSyncActionProvider
from src.sync.stores.local.local_file_store import LocalFileStoreFactory
from src.sync.stores.local.path_provider import PathProvider


class Factory:
    @staticmethod
    def create_config(logger: logging.Logger) -> StorageConfig:
        config_provider = StorageConfigProvider(logger)
        arguments = config_provider.parse_arguments()
        return config_provider.get_config(arguments)

    @staticmethod
    def create_command_handler(config: StorageConfig, logger: logging.Logger) -> CommandHandler:
        sync_service = Factory.__create_sync_service(config, logger)
        ui = CommandHandlerUi(ConsoleUi(logger), logger)
        return CommandHandler(sync_service, ui, logger)

    @staticmethod
    def __create_sync_service(config: StorageConfig, logger: logging.Logger) -> FileSyncronizationService:
        path_provider = PathProvider(config, logger)
        local_store = LocalFileStoreFactory.create(config, path_provider, logger)
        strategy = StorageStrategyFactory(local_store, logger).create(config)
        cloud_store = strategy.create_cloud_store()
        file_sync_action_provider = FileSyncActionProvider(strategy.create_file_content_comparer(), logger)
        file_mapper = FileMapper(file_sync_action_provider, logger)
        subfolder_mapper = SubfolderMapper(logger)
        folder_mapper = RecursiveFolderMapper(local_store, cloud_store, file_mapper, subfolder_mapper, config, logger)
        return FileSyncronizationService(local_store, cloud_store, folder_mapper, path_provider, config, logger)


if __name__ == '__main__':
    log = logger.setup_logger(logging.DEBUG)
    conf = Factory.create_config(log)
    commandHandler = Factory.create_command_handler(conf, log)
    commandHandler.handle(conf.action, conf.cloud_dir)
