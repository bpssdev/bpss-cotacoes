import json
import os

def readfile(path):
    try:
        with open(path, 'r', encoding='utf8') as file:
            return file.read()
    except:
        with open(path, 'r', encoding='ISO-8859-1') as file:
            return file.read()

def readfile_asjson(path):
     with open(path, mode="r") as file:
        return json.load(file)
   
       
def writefile(path, content):
    dir = os.path.dirname(path)
    createdir(dir)
   
    with open(path, 'w+', encoding='utf8') as file:
        return file.write(content)
    
def appendfile(path, content):
    dir = os.path.dirname(path)
    not_exists = not os.path.exists(dir)
    if not_exists: 
        os.mkdir(dir)

    with open(path, 'a+', encoding='utf8') as file:
        return file.write(content)

def createdir(path):
    dir_exists = os.path.exists(path)
    if dir_exists or path == "": return
    os.makedirs(path)

def deletedir(path):
    not_exists = not os.path.exists(path)
    if not_exists: return
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            deletedir(os.path.join(path, file))
        else:
            os.remove(os.path.join(path, file))
    os.rmdir(path)

def get_rootpath():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))