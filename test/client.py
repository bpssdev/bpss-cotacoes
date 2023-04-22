import win32ui
import time
import dde
import os
import uuid
from os.path import join
from threading import Thread
from pywin.mfc import object

running = False
thread = None


class Client:

    __DDEServerConnection = None
    __DDEConversations = {}

    def request(self, application, topic, item):
        try:
            if Client.__DDEServerConnection is None:
                print("creating server")
                Client.__DDEServerConnection = dde.CreateServer()
                Client.__DDEServerConnection.Create(f'{application}{uuid.uuid4()}')
            
            conversation = Client.__DDEConversations[f'{application}_{topic}'] if f'{application}_{topic}' in Client.__DDEConversations else None
            
            if conversation is None or conversation.Connected() != 1:
                print('Init conversation')
                conversation = dde.CreateConversation(Client.__DDEServerConnection)
                conversation.ConnectTo(application, topic)
                Client.__DDEConversations[f'{application}_{topic}'] = conversation
                print('is conversation connected', conversation.Connected())
            
            requested_data = conversation.Request(item)
            return requested_data
        except Exception as e:
            print(f'[cli] error - {str(e)}')

    def destroy(self):
        Client.__DDEServer.Destroy()


cli = Client()
aux = 0

try:
    while True:
        print('[cli] requensting data...')
        # time.sleep(1)
        data = cli.request('BC', "Cot", "ABC")
        print(f'[cli] {str(data)}')
        time.sleep(0.5)
        aux += 1
except Exception as e:
    print(f'[cli] outside error: {str(e)}')