#must include logger_colorer to add log highlighting
import logs.logger_colorer
import logs.logger as logger
import logging
from configs.config import ConfigProvider
from files.file_store import FileStore
from files.file_mapper import FileMapper
from stores.dropbox_store import DropboxStore
from clients.ui import UI
from clients.controller import Controller

log = logger.setupLogger(logging.DEBUG)
if __name__ == '__main__':
    configProvider = ConfigProvider(log)
    arguments = configProvider.parse_arguments()
    conf = configProvider.get_config(arguments)
    fileStore = FileStore(conf, log)
    dboxStore = DropboxStore(conf, log)
    fileMapper = FileMapper(fileStore, dboxStore, conf, log)
    ui = UI(log)
    controller = Controller(fileStore, dboxStore, fileMapper, ui, log)
    match conf.action:
        case 'download': controller.sync(conf.cloud_dir, download=True, upload=False)
        case 'upload': controller.sync(conf.cloud_dir, download=False, upload=True)
        case 'sync':   controller.sync(conf.cloud_dir, download=True, upload=True)
        case _: log.error('Unknown action in configuration')
