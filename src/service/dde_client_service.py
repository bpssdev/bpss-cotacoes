import win32ui
import uuid
import dde
 
class DdeClientService:

    def __init__(self, application) -> None:
        try:
            self.application = application
            self.server = dde.CreateServer()
            self.server.Create(f'{application}_{uuid.uuid4()}')
        except Exception as e:
            raise Exception(f"DdeClientService - Failed to find DDE Server: {application} >> " + str(e))


    def get_data(self, application, topic, item):
        try:
            conversation = dde.CreateConversation(self.server)
            conversation.ConnectTo(application, topic)
            requested_data = conversation.Request(item)
            return requested_data
        except:
            raise Exception(f"DdeClientService - Failed to recover data from server {self.server}")
        
    def destroy(self):
        self.server.Destroy()