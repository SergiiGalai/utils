import argparse
import contextlib
import os
import sys
import time
import unicodedata
import dropbox
import configparser
import logging
import pathlib
import calendar
from datetime import datetime, date
from posixpath import join as urljoin
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-6s %(filename)s:%(lineno)d %(funcName)s() %(message)s',
    datefmt='%y%m%d %H:%M:%S'
    )

logger_name = str(__file__) + " :: " + str(__name__)
logger = logging.getLogger(logger_name)
logging.getLogger("requests").setLevel(logging.WARNING)

def parse_arguments():
    logger.debug('parse_arguments started')
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file')
    parser.add_argument('--source', help='Local directory to upload')
    parser.add_argument('--dest', help='Destination folder in your Dropbox')
    parser.add_argument('--token', help='Access token (see https://www.dropbox.com/developers/apps)')
    parser.add_argument('--yes', '-y', action='store_true', help='Answer yes to all questions')
    parser.add_argument('--no', '-n', action='store_true', help='Answer no to all questions')
    parser.add_argument('--default', '-d', action='store_true', help='Take default answer on all questions')
    parser.add_argument('--action', help='download|upload|sync files (sync if not exist)')
    parser.add_argument('--dryrun', help='Do not change files if True')
    parser.add_argument('--subfolders', help='Do not change files if True')
    return parser.parse_args()

@dataclass
class Config:
    action: str
    token: str
    local_dir: str
    dbox_dir: str
    dry_run: bool
    subfolders: bool

class ConfigProvider:
    def __get_config_file_location(self, path: str):
        if path:
            return path
        else:
            return [
                    'config.ini',
                    '/etc/dbox_sync/config.ini',
                    'instance/config.ini',
                    os.path.join(os.path.expanduser('~'), '.dbox_sync_config.ini')
                    ]

    def get(self, args=None):
        logger.debug('get_config started. args={}'.format(args))

        if args is None: args = {}
        config_location = self.__get_config_file_location( args.config )
        config = configparser.ConfigParser()
        config.read( config_location )

        if not config.has_section('DBOX_SYNC'): config['DBOX_SYNC'] = {}
        config = config['DBOX_SYNC']

        action = args.action or config.get('ACTION')
        token = args.token or config.get('DROPBOX_TOKEN')
        dbox_dir = args.dest or config.get('DBOX_DIR') or ""

        local_dir = args.source or config.get('LOCAL_DIR') or ""
        if local_dir.startswith('.'):
            local_dir = os.path.abspath(local_dir)

        dry_run = args.dryrun or config.getboolean('DRY_RUN')
        subfolders = args.subfolders or config.getboolean('SUBFOLDERS')

        if sum([bool(b) for b in (args.yes, args.no, args.default)]) > 1:
            logger.error('At most one of --yes, --no, --default is allowed')
            sys.exit(2)
        if not token:
            logger.error('--token is mandatory')
            sys.exit(2)
        return Config(action, token, local_dir, dbox_dir, dry_run, subfolders)

@dataclass
class Metadata:
    client_modified: datetime
    size: int

class FileStore:
    def __init__(self, conf: Config):
        self.dry_run = conf.dry_run
        self.root_path = conf.local_dir

    def try_create_local_folder(self, path: str):
        if self.dry_run:
            logger.info('Dry Run mode. path {}'.format(path))
        else:
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def save(self, dbox_path: str, content):
        file_path = self.get_absolute_path(dbox_path)
        if self.dry_run:
            logger.info('dry run mode. Skip saving file {}'.format(file_path))
        else:
            base_path = os.path.dirname(file_path)
            self.try_create_local_folder(base_path)
            with open(file_path, 'wb') as f:
                f.write(content)
            logger.info('saved file {}...'.format(file_path))

    @staticmethod
    def __datetime_local_to_utc(t) -> datetime:
        timestamp1 = calendar.timegm(t.timetuple())
        return datetime.utcfromtimestamp(timestamp1)

    def set_modification_time(self, dbox_path: str, modified: datetime):
        file_path = self.get_absolute_path(dbox_path)
        utcModified = self.__datetime_local_to_utc(modified)

        if self.dry_run:
            logger.info('Dry Run mode. file_path {}, utcModified={}'.format(os.path.basename(file_path), utcModified))
        else:
            logger.info('file_path={}, utcModified={}'.format(file_path, utcModified))
            atime = os.stat(file_path).st_atime
            mtime = utcModified.timestamp()
            os.utime(file_path, times=(atime, mtime))

    def get_absolute_path(self, dbox_path: str) -> str:
        relative_db_path = dbox_path[1:] if dbox_path.startswith('/') else dbox_path
        result = pathlib.PurePath( self.root_path ).joinpath( relative_db_path )
        logger.debug('result={}'.format(result))
        return str(result)

    def list_folder(self, dbox_path: str):
        path = self.get_absolute_path(dbox_path)
        logger.debug('path={}'.format(path))
        if pathlib.Path(path).exists():
            root, dirs, files = next(os.walk(path))
            normalizedFiles = [unicodedata.normalize('NFC', f) for f in files]
            logger.debug('files={}'.format(normalizedFiles))
            return root, dirs, normalizedFiles
        return path, [], []

    @staticmethod
    def get_metadata(full_path: str) -> Metadata:
        mtime = os.path.getmtime(full_path)
        client_modified = datetime(*time.gmtime(mtime)[:6])
        size = os.path.getsize(full_path)
        return Metadata(client_modified, size)

    def read(self, full_path: str):
        md = self.get_metadata(full_path)
        with open(full_path, 'rb') as f:
            content = f.read()
        return content, md

class DropboxStore:
    def __init__(self, dbx, conf: Config):
        self.dbx = dbx

    def list_folder(self, dbox_path):
        logger.debug('list path: {}'.format(dbox_path))
        dirs = list()
        files = list()
        try:
            with stopwatch('list_folder'):
                res = self.dbx.files_list_folder(dbox_path)
        except dropbox.exceptions.ApiError:
            logger.warning('Folder listing failed for {} -- assumed empty'.format(dbox_path))
        else:
            for entry in res.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    files.append(entry)
                else:
                    dirs.append(entry)
        logger.debug('files={}'.format(files))
        return dbox_path, dirs, files

    def read(self, dbx_path):
        logger.debug('dbx_path={}'.format(dbx_path))
        with stopwatch('download'):
            try:
                meta_data, response = self.dbx.files_download(dbx_path)
            except dropbox.exceptions.HttpError:
                logger.exception("*** Dropbox HTTP Error")
                return None
        logger.debug('{} bytes; md: {}'.format(len(response.content), meta_data.name))
        return response, meta_data

    def save(self, dbx_path: str, content, metadata: Metadata, overwrite: bool):
        logger.debug('dbx_path={}'.format(dbx_path))
        write_mode = (dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add)
        with stopwatch('upload %d bytes' % len(content)):
            if conf.dry_run:
                logger.info('Dry run mode. Skip uploading {} (modified:{}) using {}'
                    .format(dbx_path, metadata.client_modified, write_mode))
            else:
                try:
                    res = self.dbx.files_upload(content, dbx_path, write_mode, client_modified=metadata.client_modified, mute=True)
                    logger.debug('Uploaded as {}'.format(res.name))
                    return res
                except dropbox.exceptions.ApiError:
                    logger.exception('*** API error')
                    return None

def map_files_recursive(dbox_path: str):
    logger.info('dbox_path={}'.format(dbox_path))
    local_root, local_dirs, local_files = fileStore.list_folder(dbox_path)
    dbx_root, dbx_dirs, dbx_files = dboxStore.list_folder(dbox_path)
    download_files, upload_files = map_dropbox_files_to_local(local_root, local_files, dbx_root, dbx_files)
    if conf.subfolders:
        process_folders = map_dropbox_folders_to_local(local_root, local_dirs, dbx_root, dbx_dirs)
        for dbox_folder in process_folders:
            download_sub, upload_sub = map_files_recursive(dbox_folder)
            download_files.extend(download_sub)
            upload_files.extend(upload_sub)
    return download_files, upload_files

def internal_sync(dbox_path: str, download: bool, upload: bool):
    logger.info('dbox_path={}'.format(dbox_path))
    download_files, upload_files = map_files_recursive(dbox_path)
    if download: download_dropbox_to_local_folder(download_files)
    if upload: upload_local_files_to_dropbox(upload_files)

def map_dropbox_files_to_local(local_root: str, local_files: list, dbx_root: str, dbx_files: list):
    upload_list = list()
    download_list = list()

    for dbx_file in dbx_files:
        name = dbx_file.name
        dbx_path = dbx_file.path_display

        if name in local_files:
            logger.debug('file found locally - {}'.format(name))
            local_file_path = os.path.join(local_root, name)

            if are_equal_by_date_size(local_file_path, dbx_file):
                logger.info('file {} already synced [date/size]. Skip'.format(dbx_path))
            else:
                logger.info('file {} exists with different stats. Downloading temporary'.format(dbx_path))
                response, meta_data = dboxStore.read(urljoin(dbx_root, name))
                if are_equal_by_content(local_file_path, response.content):
                    logger.info('file {} already synced [content]. Skip'.format(dbx_path))
                else:
                    md = fileStore.get_metadata(local_file_path)
                    if md.client_modified > dbx_file.client_modified:
                        logger.info('file {} has changed since last sync (dbx={} < local={}) => upload list'
                            .format(local_file_path, dbx_file.client_modified, md.client_modified))
                        upload_list.append(dbx_path)
                    else:
                        logger.info('file {} has changed since last sync (dbx={} > local={}) => download list'
                            .format(dbx_path, dbx_file.client_modified, md.client_modified))
                        download_list.append(dbx_path)
        else:
            logger.info('file NOT found locally - {} => download list'.format(dbx_path))
            download_list.append(dbx_path)

    dbx_names = list(map(lambda f: f.name, dbx_files))
    local_only = filter(lambda name: name not in dbx_names, local_files)
    for name in local_only:
        local_path = pathlib.PurePath(local_root).joinpath(name)
        logger.info('file NOT found on dropbox - {} => upload list'.format(local_path))
        dbx_path = urljoin(dbx_root, name)
        upload_list.append(dbx_path)

    return download_list, upload_list

def map_dropbox_folders_to_local(local_root: str, local_folders: list, dbx_root: str, dbx_folders: list):
    symmetric_difference = list()

    dropbox_only = filter(lambda f: f.name not in local_folders, dbx_folders)
    for folder in dropbox_only:
        dbx_path = folder.path_display
        logger.info('folder NOT found locally - {}'.format(dbx_path))
        symmetric_difference.append(dbx_path)

    dbx_names = list(map(lambda f: f.name, dbx_folders))
    local_only = filter(lambda name: name not in dbx_names, local_folders)
    for folder_name in local_only:
        local_folder_path = pathlib.PurePath(local_root).joinpath(folder_name)
        dbx_folder_path = urljoin(dbx_root, folder_name)
        logger.info('folder NOT found on dropbox - {}'.format(local_folder_path))
        symmetric_difference.append(dbx_folder_path)

    return symmetric_difference

def upload_local_files_to_dropbox(dbx_paths: list):
    if dbx_paths:
        logger.info('=== Upload files\n - {}'.format('\n - '.join(map(str, dbx_paths))))
        if yesno('Do you want to Upload files above from {}'.format(fileStore.get_absolute_path("/")), False):
            for dbx_path in dbx_paths:
                local_path = fileStore.get_absolute_path(dbx_path)
                logger.info('uploading {} => {} ...'.format(local_path, dbx_path))
                upload_file(local_path, dbx_path, overwrite=True)
        else:
            logger.info('=== upload files cancelled')
    else:
        logger.info('=== nothing to upload')

def download_dropbox_to_local_folder(dbx_paths: list):
    if dbx_paths:
        logger.info('=== Download files\n - {}'.format('\n - '.join(map(str, dbx_paths))))
        if yesno('Do you want to Download files above to {}'.format(fileStore.get_absolute_path("/")), False):
            for dbx_path in dbx_paths:
                logger.info('downloading {} => {} ...'.format(dbx_path, fileStore.get_absolute_path(dbx_path)))
                res, dbx_file = dboxStore.read(dbx_path)
                logger.debug('downloaded file: {}'.format(dbx_file))
                fileStore.save(dbx_path, res.content)
                fileStore.set_modification_time(dbx_path, dbx_file.client_modified)
        else:
            logger.info('=== download files cancelled')
    else:
        logger.info('=== nothing to download')


def sync_local_folder_to_dropbox():
    """
    Parse command line, then iterate over files and directories under
    rootdir and upload all files. Skips some temporary files and
    directories, and avoids duplicate uploads by comparing size and
    mtime with the server.
    """
    logger.debug('sync_local_folder_to_dropbox started')
    fileStore.try_create_local_folder(conf.local_dir)

    logger.debug('Walking folder {}...'.format(conf.local_dir))
    for dirname, dirs, files in os.walk(conf.local_dir):
        subfolder = dirname[len(conf.local_dir):].strip(os.path.sep)
        logger.debug('Descending into {}...'.format(subfolder))

        dbx_root, dbx_dirs, dbx_files = dboxStore.list_folder(urljoin(conf.dbox_dir, subfolder))
        logger.debug('loaded folder list from dropbox {}...'.format(dbx_files))

        # First do all the files.
        for name in files:
            local_path = os.path.join(dirname, name)
            dbx_path = urljoin(conf.dbox_dir, subfolder, name)
            nname = unicodedata.normalize('NFC', name)
            logger.debug('processing local_path={}, nname={}, dbx_path={}'.format(local_path, nname, dbx_path))
            clean_old = False

            if nname in dbx_files:
                md = dbx_files[nname]
                if are_equal_by_date_size(local_path, md):
                    logger.debug('{} is already synced [stats match]'.format(name))
                    try_cleanup(local_path, clean_old)
                else:
                    logger.debug('{} exists with different stats, downloading'.format(name))
                    res, md = dboxStore.read(dbx_path)
                    if are_equal_by_content(local_path, res.content):
                        logger.debug('{} is already synced [content match]'.format(name))
                        try_cleanup(local_path, clean_old)
                    else:
                        logger.debug('{} has changed since last sync'.format(name))
                        if yesno('Refresh {}'.format(name), False):
                            upload_file(local_path, dbx_path, overwrite=True)
            elif yesno('Upload {}'.format(name), True):
                upload_file(local_path, dbx_path, overwrite=False)

        # Then choose which subdirectories to traverse.
        keep = []
        for name in dirs:
            if name.startswith('.'):
                logger.debug('Skipping dot directory: {}'.format(name))
            elif yesno('Descend into {}'.format(name), True):
                logger.debug('Keeping directory: {}'.format(name))
                keep.append(name)
            else:
                logger.debug('OK, skipping directory: {}'.format(name))
        dirs[:] = keep


def try_cleanup(fullname, clean_old):
    if clean_old:
        os.remove(fullname)

def are_equal_by_content(fullname: str, content_dbx):
    content_local, md = fileStore.read(fullname)
    return content_dbx == content_local

def are_equal_by_date_size(file_path: str, dbox_file):
    if isinstance(dbox_file, dropbox.files.FileMetadata):
        md = fileStore.get_metadata(file_path)
        are_equal_by_size = (md.size == dbox_file.size)
        if not are_equal_by_size:
            logger.info('file={} not equal by size: local={}, remote={}'
            .format(os.path.basename(file_path), md.size, dbox_file.size))
            return False

        are_equal_by_date = (md.client_modified == dbox_file.client_modified)
        if not are_equal_by_date:
            logger.info('file={} not equal by date: local={}, remote={}'
            .format(os.path.basename(file_path), md.client_modified, dbox_file.client_modified))
            return False

        return True
    else:
        logger.warn('{} is not a dropbox file'.format(dbox_file))
    return False

def upload_file(local_path, dbx_path, overwrite):
    logger.debug('local_path={}, dbx_path={}'.format(local_path, dbx_path))
    content, md = fileStore.read(local_path)
    dboxStore.save(dbx_path, content, md, overwrite)

def yesno(message, default):
    """Handy helper function to ask a yes/no question.

    Command line arguments --yes or --no force the answer;
    --default to force the default answer.

    Otherwise a blank line returns the default, and answering
    y/yes or n/no returns True or False.

    Retry on unrecognized answer.

    Special answers:
    - q or quit exits the program
    - p or pdb invokes the debugger
    """
    if args.default:
        logger.debug('{} ? [auto] {}'.format(message, 'Y' if default else 'N'))
        return default
    if args.yes:
        logger.debug('{} ? [auto] YES'.format(message))
        return True
    if args.no:
        logger.debug('{} ? [auto] NO'.format(message))
        return False
    if default:
        message += '? [Y/n] '
    else:
        message += '? [N/y] '
    while True:
        logger.debug('--')
        user_answer = input(message)
        answer = user_answer.strip().lower() if user_answer else None

        if not answer:
            return default
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False
        if answer in ('q', 'quit'):
            logger.warning('Exit')
            raise SystemExit(0)
        if answer in ('p', 'pdb'):
            import pdb
            pdb.set_trace()
        logger.debug('Please answer YES or NO.')

@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        logger.debug('Total elapsed time for {}: '
                     '{:.3f}'.format(message, t1 - t0))

if __name__ == '__main__':
    args = parse_arguments()
    conf = ConfigProvider().get(args)
    fileStore = FileStore(conf)
    dbx = dropbox.Dropbox(conf.token)
    dboxStore = DropboxStore(dbx, conf)
    if conf.action == 'download': internal_sync(conf.dbox_dir, download=True, upload=False)
    elif conf.action == 'upload': internal_sync(conf.dbox_dir, download=False, upload=True)
    elif conf.action == 'sync':   internal_sync(conf.dbox_dir, download=True, upload=True)
    else: logger.error('Unknown action in configuration')
