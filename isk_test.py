import os
from xmlrpclib import ServerProxy

server = ServerProxy("http://localhost:31128/RPC")
data_dir = "/home/gan/download/pic_dataset/"

def init_db():
    server.createDb(1)
    for d in os.listdir(data_dir):
        f = os.path.join(data_dir, d) 
        if os.path.isfile(f) and d.endswith(".jpg"):
            id = int(d.split('.')[-2])
            server.addImg(1, id, f)
    server.saveAllDbs()

#init_db()
#server.saveAllDbs()
#server.loadAllDbs()

res = server.getDbImgCount(1)
print res
#res = server.getAllImgsByKeywords(1, 30, 1, '3')
res = server.queryImgID(1, 484)
print res
