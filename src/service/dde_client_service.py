import win32ui
import uuid
import dde
 
class DdeClientService:

    __DDEServer = None

    def __init__(self, application) -> None:
        try:
            self.application = application
            if DdeClientService.__DDEServer is None
                DdeClientService.__DDEServer = dde.CreateServer()
                DdeClientService.__DDEServer.Create(f'{application}_{uuid.uuid4()}')
        except Exception as e:
            raise Exception(f"[dde_client_service] - Failed to find DDE Server: {application} >> " + str(e))


    def get_data(self, application, topic, item):
        try:
            conversation = dde.CreateConversation(DdeClientService.__DDEServer)
            conversation.ConnectTo(application, topic)
            requested_data = conversation.Request(item)
            return requested_data
        except:
            raise Exception(f"[dde_client_service] - Failed to recover data from server {self.application}")
        