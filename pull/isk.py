import os
from xmlrpclib import ServerProxy
from django.conf import settings
import random

server = ServerProxy("http://localhost:31128/RPC")
data_dir = settings.DATA_DIR

def get_all_db():
    pics = []
    for d in os.listdir(data_dir):
        f = os.path.join(data_dir, d) 
        if os.path.isfile(f) and d.endswith(".jpg"):
            id = int(d.split('.')[-2])
            pics.append({'id':id, 'path':f})
    return pics

data_pic = get_all_db()

def init_pic_db():
    for pic in data_pic:
        server.addImg(1, pic['id'], pic['path'])
    server.saveAllDbs()

def add_pic():
    server.addImg(1, 999991, os.path.join(data_dir, '999991.jpg'))
    server.addImg(1, 999990, os.path.join(data_dir, '999990.jpg'))

#server.createDb(1)
#server.resetDb(1)
#print 'img count', server.getDbImgCount(1)
#add_pic()
#init_pic_db()
#print 'img count after creating', server.getDbImgCount(1)

def query_img(id):
    res = server.queryImgID(1, id)
    results = []
    url_base = '/static/pic/'
    if id == 0:
        for p in random.sample(data_pic, 50):
            results.append({'id':p['id'], 'url': '%s%d.jpg'%(url_base,p['id']), 'sim':'0.0'})
    else:
        for p in res[0:12]:
            results.append({'id':p[0], 'url': '%s%d.jpg'%(url_base,p[0]), 'sim':'%.2f'%p[1]})
    return results

#print query_img(0)
