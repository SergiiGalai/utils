from dataclasses import dataclass
from datetime import datetime

@dataclass
class CloudFolderMetadata:
    id: str
    name: str
    path_lower: str
    path_display: str

@dataclass
class CloudFileMetadata:
    id: str
    name: str
    path_display: str
    client_modified: datetime
    size: int
    
@dataclass
class LocalFileMetadata:
    name: str
    cloud_path: str
    full_path: str
    client_modified: datetime
    size: int
