from dataclasses import dataclass
from datetime import datetime

@dataclass
class CloudFolderMetadata:
    path_lower: str
    path_display: str

@dataclass
class CloudFileMetadata:
    name: str
    path_display: str
    client_modified: datetime
    size: int
