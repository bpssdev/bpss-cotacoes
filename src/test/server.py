import win32ui
import time
import dde
import uuid
from os.path import join
from threading import Thread
from pywin.mfc import object
import inspect

running = False
thread = None
class DDETopic(object.Object):
    
    def __init__(self, topicName):
        self.topic = dde.CreateTopic(topicName)
        object.Object.__init__(self, self.topic)
        self.items = {}

    def setData(self, itemName, value):
        try:
            self.items[itemName].SetData( str(value) )
        except KeyError:
            if itemName not in self.items:
                self.items[itemName] = dde.CreateStringItem(itemName)
                self.topic.AddItem( self.items[itemName] )
                self.items[itemName].SetData( str(value) )


class Server:

    def start(self):
        def job(): 
            print("[server] start")
            running = True
            ddeServer = dde.CreateServer()
            ddeServer.Create('BC')
            ddeTopic = DDETopic('Cot')
            ddeServer.AddTopic(ddeTopic)

            value = 0
            while running:
                yourData = value
                value += 2
                ddeTopic.setData('ABC', yourData)
                print(f'[server] {inspect.stack()[1][3]} on dde: {str(value)}')
                win32ui.PumpWaitingMessages(0, -1)
                time.sleep(2)
            print("[server] end")
    
        thread = Thread(target=job, name=f'job_{uuid.uuid4()}')
        thread.start()

Server().start()