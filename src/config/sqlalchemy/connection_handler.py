from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import oracledb
import os
from utils.configuration import Configuration

class ConnectionHandler:

    def __init__(self) -> None:
        self.configuration = Configuration()
        self.__host = f"{self.configuration.host}:{self.configuration.port}"
        self.__service = self.configuration.service
        self.__username = self.configuration.username
        self.__password = self.configuration.password

        self.__engine = self.__create_database_engine()
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
        return engine

    def get_engine(self):
        return self.__engine
    
    def __enter__(self):
        session_make = sessionmaker(bind=self.__engine)
        self.session = session_make()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


