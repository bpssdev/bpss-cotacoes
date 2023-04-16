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

    __DDEServer = None

    def request(self, application, topic, item):
        try:
            if Client.__DDEServer is None:
                Client.__DDEServer = dde.CreateServer()
                Client.__DDEServer.Create(f'{application}{uuid.uuid4()}')
            
            conversation = dde.CreateConversation(Client.__DDEServer)
            conversation.ConnectTo(application, topic)

            requested_data = conversation.Request(item)
            return requested_data
        except Exception as e:
            print(f'[cli] error - {str(e)}')

    def destroy(self):
        Client.__DDEServer.Destroy()


cli = Client()
aux = 0

try:
    while aux < 10:
        print('[cli] requensting data...')
        # time.sleep(1)
        data = cli.request('BC', "Cot", "ABC")
        print(f'[cli] {str(data)}')
        # time.sleep(1)
        aux += 1
except Exception as e:
    print(f'[cli] outside error: {str(e)}')