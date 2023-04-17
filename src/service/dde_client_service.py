import win32ui
import uuid
import dde
import logging

class DdeClientService:

    __DDEServer = None

    def __init__(self, application) -> None:
        self.logger = logging.getLogger(__name__)
        try:
            self.application = application
            if DdeClientService.__DDEServer is None:
                DdeClientService.__DDEServer = dde.CreateServer()
                DdeClientService.__DDEServer.Create(f'{application}_{uuid.uuid4()}')
                self.logger.debug('DdeClientService initialized')
        except Exception as e:
            raise Exception(f"Failed to initialize DdeClientService: {application} >> " + str(e))


    def get_data(self, application, topic, item):
        try:
            self.logger.debug(f'application: {application}, topic: {topic}, item: {item}')
            conversation = dde.CreateConversation(DdeClientService.__DDEServer)
            conversation.ConnectTo(application, topic)
            self.logger.debug(f'Connected with dde application: {application}, topic: {topic}, item: {item}')
            requested_data = conversation.Request(item)
            self.logger.debug(f'Recoverd data: {str(requested_data)}')
            return requested_data
        except Exception as e:
            self.logger.debug(str(e))
            self.logger.info(f'Failed to recover data from dde server, returning None as value')
            return None
        