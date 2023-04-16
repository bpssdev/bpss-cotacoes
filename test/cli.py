import win32ui
import win32dde
import time
import dde
from utils.file import readfile_asjson
from os.path import join
 
try:
    config = readfile_asjson(join("config", "config.json"))
    application, topic, item = config['dde'].values()

    print("Params:", application, topic, item, config['dde'])

    client = win32dde.DDEClient(application, topic)
    client.connect()

    while True:
        try:
            time.sleep(2)
            requested_data = client.request(item)
            print(requested_data)
        except Exception as e:
            print(e)

except Exception as e:
    print(e)
