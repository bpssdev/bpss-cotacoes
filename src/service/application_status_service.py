from datetime import datetime
from dataclasses import dataclass
from typing import Type
from utils.file import readfile_asjson, writefile
import os
import json

@dataclass
class ApplicationStatus:
    last_update: datetime
    
class ApplicationStatusService:

    def __init__(self) -> None:
        self.status_file = os.path.join("tmp", "status.json")

    def get_status(self):
        file_not_exists = not os.path.exists(self.status_file)
        if file_not_exists:
            return ApplicationStatus(
                last_update=None
            )    

        status_json = readfile_asjson(self.status_file)
        return ApplicationStatus(
            last_update=datetime.strptime(status_json["lastUpdate"], '%Y-%m-%dT%H:%M:%S.%f') if not status_json["lastUpdate"] is None else None
        )
    
    def update_status(self, status: Type[ApplicationStatus]):
        writefile(self.status_file, json.dumps({
            "lastUpdate": status.last_update.isoformat()
        }, indent=4))

