from threading import Thread
import uuid
from tkinter import messagebox

def run_async(fn, logger, onerror_fn=None):
    taskname = f'job_{uuid.uuid4()}'
    def job(): 
        try:
            fn()
        except Exception as exception:
            print(exception)
            logger.info(exception)
            if not onerror_fn is None:
                onerror_fn(exception)
        
    thread = Thread(target=job, name=taskname)
    thread.start()
    