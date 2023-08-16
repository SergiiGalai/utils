#must include logger_colorer to add log highlighting
import code.logs.logger_colorer
import code.logs.logger as logger
import logging
from code.configs.config import ConfigProvider
from code.files.file_store import FileStore
from code.files.file_mapper import FileMapper
from code.stores.dropbox_store import DropboxStore
from code.clients.ui import UI
from code.clients.controller import Controller

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
