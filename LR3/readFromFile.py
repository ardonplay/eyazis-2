import os


def LoadFile():
    dirName = os.path.abspath("texts/")
    files = os.listdir("texts/")
    string = ''.join(files)
    file = (dirName + '/' + string)
   # print(file)
    return file


def readFromFile():
    file = open(LoadFile(), "r")
    content = file.read()
    #print(content)
    return content
