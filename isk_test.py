import os
from xmlrpclib import ServerProxy

server = ServerProxy("http://localhost:31128/RPC")
data_dir = "/home/gan/download/pic_dataset/"

file_img = '/home/janson/download/z2.jpg'

file_dir = '/home/janson/download/testimg'
thumb = 'thumb'
data_dir = os.path.join(file_dir, thumb)

def init_db2():
    server.createDb(1)
    for d in os.listdir(data_dir):
        f = os.path.join(data_dir, d)
        if os.path.isfile(f) and d.endswith(".jpeg"):
            id = int(d.split('.')[-2])
            server.addImg(1, id, f)
    server.saveAllDbs()

def init_db():
    id = 1
    f = file_img
    server.createDb(1)
    server.addImg(1, id, f)
    server.saveAllDbs()

#init_db2()
#server.saveAllDbs()
#server.loadAllDbs()

#res = server.getDbImgCount(1)
#print res
#res = server.getAllImgsByKeywords(1, 30, 1, '3')
res = server.queryImgID(1, 1)
print res
