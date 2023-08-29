from dataclasses import dataclass
from datetime import datetime

@dataclass
class CloudFolderMetadata:
    id: str
    name: str
    path_lower: str
    cloud_path: str

@dataclass
class CloudFileMetadata:
    id: str
    name: str
    cloud_path: str
    client_modified: datetime
    size: int
    content_hash: str
    
@dataclass
class LocalFileMetadata:
    name: str
    cloud_path: str
    local_path: str
    client_modified: datetime
    size: int
