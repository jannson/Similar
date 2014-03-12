import sys, os, os.path
import codecs
import json

django_path = '/home/gan/project/source/svn_project/pull/1'
sys.path.insert(13, django_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pull.settings'

from django.db.models import Count
from django.db.models import Q
from pull.models import HtmlContent

class JsonObj(object):
    def __init__(self, id,title,content):
        self.id = id
        self.title = title
        self.content = content

def dump_test():
    with open('db.txt', 'w') as file:
        file.write('[')
        start = True
        for obj in HtmlContent.objects.filter(~Q(retry=3)).filter(~Q(content='')):
            str_json = ''
            if start:
                str_json = '{"id":'
                start = False
            else:
                str_json = ',{"id":'
            str_json += str(obj.id)+',"title":'+json.JSONEncoder().encode(obj.title)
            str_json += ',"content":'+json.JSONEncoder().encode(obj.content)+'}'
            file.write(str_json)
        file.write(']')

def dump_test2():
    objs = HtmlContent.objects.filter(status=0).filter(~Q(content=''))
    print 'len:', len(objs)

dump_test2()
