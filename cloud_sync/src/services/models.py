from dataclasses import dataclass
from enum import Enum

from src.stores.models import FileMetadata


class FileAction(Enum):
   DOWNLOAD = 1
   UPLOAD = 2
   SKIP = 3
   CONFLICT = 4

class FileComparison(Enum):
   ERROR = 1
   EQUAL = 2
   DIF_BY_NAME = 3
   DIF_BY_SIZE = 4
   DIF_BY_DATE = 5

