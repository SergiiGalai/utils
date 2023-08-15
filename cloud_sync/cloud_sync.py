import logging
import logger
from config import ConfigProvider
from dropbox_store import FileStore, DropboxStore, FileMapper
from ui import UI
from controller import Controller

log = logger.setupLogger(logging.WARNING)
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
