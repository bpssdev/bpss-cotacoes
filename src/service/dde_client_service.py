import win32ui
import uuid
import dde
import logging

class DdeClientService:

    __DDEServerConnection = None
    __DDEConversations = {}

    def __init__(self, application) -> None:
        self.logger = logging.getLogger(__name__)
        try:
            self.application = application
            if DdeClientService.__DDEServerConnection is None:
                DdeClientService.__DDEServerConnection = self.__create_server(application)
                self.logger.debug('DdeClientService initialized')
        except Exception as e:
            raise Exception(f"Failed to initialize DdeClientService: {application} >> " + str(e))

    def __create_server(self, application):
        server = dde.CreateServer()
        server.Create(f'{application}_{uuid.uuid4()}')
        return server

    def get_data(self, application, topic, item):
        try:
            self.logger.debug(f'application: {application}, topic: {topic}, item: {item}')

            conversation = DdeClientService.__DDEConversations[f'{application}_{topic}'] if f'{application}_{topic}' in DdeClientService.__DDEConversations else None
            
            if conversation is None or conversation.Connected() != 1:
                self.logger.debug('Conversation initialized')
                conversation = dde.CreateConversation(DdeClientService.__DDEServerConnection)
                conversation.ConnectTo(application, topic)
                DdeClientService.__DDEConversations[f'{application}_{topic}'] = conversation
                self.logger.debug(f'is conversation connected {str(conversation.Connected())}')
            
            self.logger.debug(f'Connected with dde application: {application}, topic: {topic}, item: {item}')
            requested_data = conversation.Request(item)
            self.logger.debug(f'Recoverd data: {str(requested_data)}')
            return requested_data
        except Exception as e:
            self.logger.debug(str(e))
            self.logger.info(f'Failed to recover data from dde server, returning None as value')
            return None
        