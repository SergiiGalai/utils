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

def get_config_file_location(path: str):
    if path:
        config_location = path
    else:
        config_location = [
                'config.ini',
                '/etc/dbox_sync/config.ini',
                'instance/config.ini',
                os.path.join(os.path.expanduser('~'), '.dbox_sync_config.ini')
                ]
    return config_location

def get_config(args=None):
    logger.debug('get_config started. args={}'.format(args))

    if args is None: args = {}

    config_location = get_config_file_location( args.config )
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

def download_dropbox_to_local_folder_without_recurse(root_local_path: str, dbox_path: str): internal_sync(root_local_path, dbox_path, True, False)
def upload_local_folder_to_dropbox_without_recurse(root_local_path: str, dbox_path: str): internal_sync(root_local_path, dbox_path, False, True)
def sync_local_foler_with_dropbox_without_recurse(root_local_path: str, dbox_path: str): internal_sync(root_local_path, dbox_path, True, True)
def internal_sync(root_local_path: str, dbox_path: str, download: bool, upload: bool):
    logger.info('root_local_path={}, dbox_path={}'.format(root_local_path, dbox_path))

    local_root, local_dirs, local_files = read_local_folder( get_absolute_local_path(root_local_path, dbox_path) )
    dbx_root, dbx_dirs, dbx_files = read_dropbox_folder(dbox_path)

    download_files, upload_files = map_dropbox_files_to_local(local_root, local_files, dbx_root, dbx_files)
    if conf.subfolders:
        process_folders = map_dropbox_folders_to_local(local_root, local_dirs, dbx_root, dbx_dirs)

    if download: download_dropbox_to_local_folder(root_local_path, download_files)
    if upload: upload_local_files_to_dropbox(root_local_path, upload_files)

def get_absolute_local_path(root_local_path: str, dbox_path: str):
    relative_db_path = dbox_path[1:] if dbox_path.startswith('/') else dbox_path
    result = pathlib.PurePath(root_local_path).joinpath(relative_db_path)
    logger.info('result={}'.format(result))
    return str(result)

def try_create_local_folder(path: str):
    if conf.dry_run:
        logger.info('Dry Run mode. path {}'.format(path))
    else:
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

def read_local_folder(path: str):
    logger.debug('path={}'.format(path))
    if pathlib.Path(path).exists():
        root, dirs, files = next(os.walk(path))
        normalizedFiles = [unicodedata.normalize('NFC', f) for f in files]
        logger.debug('files={}'.format(normalizedFiles))
        return root, dirs, normalizedFiles
    return path, [], []

def read_dropbox_folder(path: str):
    logger.debug('path={}'.format(path))
    root, dirs, files = list_dropbox_folder(dbx, path)
    logger.debug('files={}'.format(files))
    return root, dirs, files

def map_dropbox_files_to_local(local_root: str, local_files: list, dbx_root: str, dbx_files: list):
    upload_list = list()
    download_list = list()

    for dbx_file in dbx_files:
        name = dbx_file.name
        dbx_path = dbx_file.path_lower

        if name in local_files:
            logger.debug('file found locally - {}'.format(name))
            local_file_path = os.path.join(local_root, name)

            if are_equal_by_date_size(local_file_path, dbx_file):
                logger.info('file {} already synced [date/size]. Skip'.format(dbx_path))
            else:
                logger.info('file {} exists with different stats. Downloading temporary'.format(dbx_path))
                response, meta_data = download_file(dbx, urljoin(dbx_root, name))
                if are_equal_by_content(local_file_path, response.content):
                    logger.info('file {} already synced [content]. Skip'.format(dbx_path))
                else:
                    localfile_modified = get_file_modified_time(local_file_path)
                    if localfile_modified > dbx_file.client_modified:
                        logger.info('file {} has changed since last sync (dbx={} < local={}) => upload list'
                            .format(local_file_path, dbx_file.client_modified, localfile_modified))
                        upload_list.append(dbx_path)
                    else:
                        logger.info('file {} has changed since last sync (dbx={} > local={}) => download list'
                            .format(dbx_path, dbx_file.client_modified, localfile_modified))
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
        dbx_path = folder.path_lower
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

def upload_local_files_to_dropbox(root_local_path:str, dbx_paths: list):
    if dbx_paths and yesno('=== Upload files {}'.format(dbx_paths), False):
        for dbx_path in dbx_paths:
            local_path = get_absolute_local_path(root_local_path, dbx_path)
            logger.info('uploading {}=>{}...'.format(local_path, dbx_path))
            upload_file(dbx, local_path, dbx_path, overwrite=True)
    else:
        logger.info('=== upload files skipped')

def download_dropbox_to_local_folder(root_local_path:str, dbx_paths: list):
    if dbx_paths and yesno('=== Download files {}'.format(dbx_paths), False):
        for dbx_path in dbx_paths:
            file_local_path = get_absolute_local_path(root_local_path, dbx_path)
            logger.info('downloading {}=>{}...'.format(dbx_path, file_local_path))
            res, dbx_file = download_file(dbx, dbx_path)
            logger.debug('downloaded file: {}'.format(dbx_file))
            save_binary_file(file_local_path, res.content)
            set_modification_time_from_dropbox(file_local_path, datetime_local_to_utc(dbx_file.client_modified))
    else:
        logger.info('=== download files skipped')

def save_binary_file(file_path: str, content):
    if conf.dry_run:
        logger.info('dry run mode. Skip saving file {}'.format(file_path))
    else:
        base_path = os.path.dirname(file_path)
        try_create_local_folder(base_path)
        with open(file_path, 'wb') as f:
            f.write(content)
        logger.info('saved file {}...'.format(file_path))

def set_modification_time_from_dropbox(file_path: str, modified: datetime):
    mtime = modified.timestamp()
    if conf.dry_run:
        logger.info('Dry Run mode. file_path {}, modified={}'.format(os.path.basename(file_path), modified))
    else:
        logger.info('file_path={}, modified={}'.format(file_path, modified))
        atime = os.stat(file_path).st_atime
        os.utime(file_path, times=(atime, mtime))


def sync_local_folder_to_dropbox():
    """
    Parse command line, then iterate over files and directories under
    rootdir and upload all files. Skips some temporary files and
    directories, and avoids duplicate uploads by comparing size and
    mtime with the server.
    """
    logger.debug('sync_local_folder_to_dropbox started')
    try_create_local_folder(conf.local_dir)

    logger.debug('Walking folder {}...'.format(conf.local_dir))
    for dirname, dirs, files in os.walk(conf.local_dir):
        subfolder = dirname[len(conf.local_dir):].strip(os.path.sep)
        logger.debug('Descending into {}...'.format(subfolder))

        dbx_root, dbx_dirs, dbx_files = list_dropbox_folder(dbx, urljoin(conf.dbox_dir, subfolder))
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
                    res, dbx_file = download_file(dbx, dbx_path)
                    if are_equal_by_content(local_path, res.content):
                        logger.debug('{} is already synced [content match]'.format(name))
                        try_cleanup(local_path, clean_old)
                    else:
                        logger.debug('{} has changed since last sync'.format(name))
                        if yesno('Refresh {}'.format(name), False):
                            upload_file(dbx, local_path, dbx_path, overwrite=True)
            elif yesno('Upload {}'.format(name), True):
                upload_file(dbx, local_path, dbx_path)

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
    with open(fullname, 'rb') as f:
        content_local = f.read()
    return content_dbx == content_local

def get_file_modified_time(file_path: str) -> datetime:
    mtime = os.path.getmtime(file_path)
    dt = time.gmtime(mtime)[:6]
    return datetime(*dt)

def are_equal_by_date_size(file_path: str, dbox_file):
    mtime_dt = get_file_modified_time(file_path)
    size = os.path.getsize(file_path)

    if isinstance(dbox_file, dropbox.files.FileMetadata):
        are_equal_by_size = (size == dbox_file.size)
        if not are_equal_by_size:
            logger.info('file={} not equal by size: local={}, remote={}'
            .format(os.path.basename(file_path), size, dbox_file.size))
            return False

        are_equal_by_date = (mtime_dt == dbox_file.client_modified)
        if not are_equal_by_date:
            logger.info('file={} not equal by date: local={}, remote={}'
            .format(os.path.basename(file_path), mtime_dt, dbox_file.client_modified))
            return False

        return True
    else:
        logger.warn('{} is not a dropbox file'.format(dbox_file))
    return False

def list_dropbox_folder(dbx, dbox_path):
    logger.debug('list path: {}'.format(dbox_path))
    dirs=list()
    files=list()

    try:
        with stopwatch('list_folder'):
            res = dbx.files_list_folder(dbox_path)
    except dropbox.exceptions.ApiError:
        logger.warning('Folder listing failed for {} -- assumed empty'.format(dbox_path))
    else:
        for entry in res.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                files.append(entry)
            else:
                dirs.append(entry)
    return dbox_path, dirs, files

def download_file(dbx, dbx_path):
    logger.debug('dbx_path={}'.format(dbx_path))
    with stopwatch('download'):
        try:
            meta_data, response = dbx.files_download(dbx_path)
        except dropbox.exceptions.HttpError:
            logger.exception("*** Dropbox HTTP Error")
            return None
    logger.debug('{} bytes; md: {}'.format(len(response.content), meta_data.name))
    return response, meta_data

def upload_file(dbx, local_path, dbx_path, overwrite=False):
    logger.debug('local_path={}, dbx_path={}'.format(local_path, dbx_path))

    mtime = os.path.getmtime(local_path)
    client_modified = datetime(*time.gmtime(mtime)[:6])
    write_mode = (dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add)

    with open(local_path, 'rb') as f:
        content = f.read()

    with stopwatch('upload %d bytes' % len(content)):
        if conf.dry_run:
            logger.info('Dry run mode. Skip uploading {} => {} (modified:{}) using {}'
                .format(local_path, dbx_path, client_modified, write_mode))
        else:
            try:
                res = dbx.files_upload(content, dbx_path, write_mode, client_modified=client_modified, mute=True)
                logger.debug('Uploaded as {}'.format(res.name))
                return res
            except dropbox.exceptions.ApiError:
                logger.exception('*** API error')
                return None

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

def datetime_local_to_utc(t):
    timestamp1 = calendar.timegm(t.timetuple())
    return datetime.utcfromtimestamp(timestamp1)

if __name__ == '__main__':
    args = parse_arguments()
    conf = get_config(args)
    dbx = dropbox.Dropbox(conf.token)

    if conf.action == 'download':
        download_dropbox_to_local_folder_without_recurse(conf.local_dir, conf.dbox_dir)
    elif conf.action == 'upload':
        upload_local_folder_to_dropbox_without_recurse(conf.local_dir, conf.dbox_dir)
    else:
        sync_local_foler_with_dropbox_without_recurse(conf.local_dir, conf.dbox_dir)
