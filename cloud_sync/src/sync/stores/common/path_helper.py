import os


def strip_starting_slash(path: str) -> str:
    return path[1:] if path.startswith('/') else path


def start_with_slash(path: str) -> str:
    return path if path.startswith('/') else '/' + path


def get_file_extension(path: str) -> str:
    _, extension = os.path.splitext(path)
    return extension


def get_file_name(path: str) -> str:
    return os.path.basename(path)
