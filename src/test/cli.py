import win32ui
import time
import dde
from utils.file import readfile_asjson
from os.path import join
 
try:
    config = readfile_asjson(join("config", "config.json"))
    application, topic, item = config['dde'].values()

    print("Params:", application, topic, item, config['dde'])

    server = dde.CreateServer()
    server.Create(application)
    conversation = dde.CreateConversation(server)
    conversation.ConnectTo(application, topic)

    while True:
        try:
            time.sleep(2)
            requested_data = conversation.Request(item)
            print(requested_data)
        except Exception as e:
            print(e)

except Exception as e:
    print(e)
