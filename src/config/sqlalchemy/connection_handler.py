from utils.configuration import configuration

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import oracledb


class ConnectionHandler:

    __ENGINE = None

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.configuration = configuration
        self.__host = f"{self.configuration.host}:{self.configuration.port}"
        self.__service = self.configuration.service
        self.__username = self.configuration.username
        self.__password = self.configuration.password
        
        if ConnectionHandler.__ENGINE is None:
            self.logger.debug('ConnectionHandler initialized')
            ConnectionHandler.__ENGINE = self.__create_database_engine()
        self.session = None

    def __create_database_engine(self):
        cp = oracledb.ConnectParams()
        oracledb.init_oracle_client()
        cp.parse_connect_string(f"{self.__host}/{self.__service}")
        thick_mode = None
        # f'oracle+oracledb://{self.__username}:{self.__password}@{cp.host}:{cp.port}/?service_name={cp.service_name}'
        engine = create_engine(
            f'oracle+oracledb://{self.__username}:{self.__password}@{cp.host}:{cp.port}{"/" if self.configuration.type_of_connection == "SID" else "/?service_name="}{cp.service_name}',
            thick_mode=thick_mode, 
            echo=False)
        self.logger.debug('Engine created')
        return engine

    def get_engine(self):
        return ConnectionHandler.__ENGINE
    
    def __enter__(self):
        session_make = sessionmaker(bind=ConnectionHandler.__ENGINE)
        self.session = session_make()
        self.logger.debug('Session initialized')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.logger.debug('Session closed')


