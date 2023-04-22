import gui.view as view
from utils.configuration import configuration
from utils.file import createdir
import logging
from logging.handlers import RotatingFileHandler

createdir('log')
createdir("tmp")

log_file_name = 'log/' + 'application_[debug].log' if configuration.level_log == 'DEBUG' else 'application.log'
log_handler = RotatingFileHandler(
    log_file_name, 
    mode='a', 
    maxBytes=1024*1024*1024, 
    backupCount=2, 
    encoding=None, 
    delay=0
)
log_handler.setFormatter(logging.Formatter(
    fmt='%(asctime)s [%(levelname)s][%(name)s]: %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
))
log_handler.setLevel(
    logging.INFO if configuration.level_log == 'INFO' else \
    logging.DEBUG if configuration.level_log == 'DEBUG' else\
    logging.NOTSET
)


logging.basicConfig(
    handlers=[log_handler],
    format='%(asctime)s [%(levelname)s][%(name)s]: %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    level=configuration.level_log,
)

view.Application().start()
