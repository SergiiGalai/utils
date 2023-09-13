
class PathHelper:

    @staticmethod
    def strip_starting_slash(path):
        return path[1:] if path.startswith('/') else path

    @staticmethod
    def start_with_slash(path):
        return path if path.startswith('/') else '/' + path
