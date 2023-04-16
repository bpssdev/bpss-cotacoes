import os
from utils.file import get_rootpath, readfile_asjson

class Configuration:

    def __init__(self) -> None:
        self.configuration_file = "application_config.json"
        if not os.path.exists(self.configuration_file): raise Exception("Failed to load configuration file: application_config.json")
        
        configuration_json = readfile_asjson(self.configuration_file)
        database_configuration_json = configuration_json["database"]

        self.host = database_configuration_json['host']
        self.port = database_configuration_json['port']
        self.service = database_configuration_json['service']
        self.username = database_configuration_json['username']
        self.password = database_configuration_json['password']
        self.type_of_connection = 'SID' if database_configuration_json["isConnectionSid"] == True else 'SERVICE'

        self.level_log = configuration_json["levelLog"]
        self.test_mode = configuration_json["testMode"]

configuration = Configuration()
        
        
