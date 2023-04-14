from .file import appendfile
from datetime import datetime  
from dataclasses import asdict
import json

class Logger:

    def __init__(self, filename) -> None:
        self.filename = filename

    def info(self, content):
        appendfile(self.filename, f'{datetime.now()}\t\t{content}\n')

    def json(self, content):
        appendfile(self.filename, f'{datetime.now()}\t\t{json.dumps(content.__dict__, indent=4)}\n')
