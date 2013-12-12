# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django import forms
from django.shortcuts import render_to_response
from django.http import HttpResponse
#from django.views.generic.list_detail import object_list
from django.views.generic import ListView
from django.db.models import Count
from django.db.models import Q
from django.db import connection
from django.utils.http import urlquote_plus, urlquote
#import simplejson as json
import json
import urllib2
import redis
import django_rq
from rq.job import Job
from hashes.simhash import simhash as simhashpy
from cppjiebapy import Tokenize

from django.db.models import Q

#from settings import *
from django.conf import settings
from pull.models import *
from extract import TextExtract, TextToHtml, ContentEncodingProcessor, USER_AGENT
from summ import summarize, sim_search, sim_content, sim_index, id2cls_func

# Default values.
REDIS_URL = None
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_KEY = 'groud_crawler:start_urls'
def get_redis_server():
    #url = settings.get('REDIS_URL',  REDIS_URL)
    #host = settings.get('REDIS_HOST', REDIS_HOST)
    #port = settings.get('REDIS_PORT', REDIS_PORT)
    url = REDIS_URL
    host = REDIS_HOST
    port = REDIS_PORT

    # REDIS_URL takes precedence over host/port specification.
    if url:
        return redis.from_url(url)
    else:
        return redis.Redis(host=host, port=port)

redis_server = get_redis_server()
def redis_queue(url):
    redis_server.rpush(REDIS_KEY, url)

#default_queue = django_rq.get_queue('default')
#html_remove = re.compile(r'\s*<.*?>\s*',re.I|re.U|re.S)

def proxy_task(id):
    try:
        html = HtmlContent.objects.get(pk=id)
        #print 'html content', html.content
        if html.status <= 1 and html.content != '':
            return html.status
    except:
        # Not find
        return HttpResponse('not find')

    the_data = ''
    try:
        req = urllib2.Request(html.url)
        req.add_header('User-Agent', USER_AGENT)
        encoding_support = ContentEncodingProcessor
        opener = urllib2.build_opener(encoding_support, urllib2.HTTPHandler)
        #print 'requesting'
        proxied_request = opener.open(req, timeout=12)
        content = proxied_request.read()
        #print 'requested'
    except urllib2.HTTPError as e:
        html.status = 3
        print 'urllib2 error'
    else:
        try:
            ucontent = content.decode('utf-8')
        except UnicodeDecodeError:
            ucontent = content.decode('gbk','ignore')
        #print 'parsing'
        tx = TextExtract(ucontent)
        #print 'parsed'
        html.title = tx.title
        html.content = tx.content.strip()
        if tx.content == '':
            print 'Parse html error'
            html.status = 4
        else:
            html.status = 0
            html.hash = long(simhashpy(list(Tokenize(html.content))))
            html.tags,html.summerize = summarize(html.content)
            if len(html_remove.sub('', tx.preview)) < 250:
                html.preview = TextToHtml(tx.content)
            else:
                html.preview = tx.preview

    #print html.id, html.title, html.tags, html.summerize
    html.save()
    if html.status == 0:
        print 'begin sim_index'
        #sim_index(html)

    return html.status

def task_to(request, id):
    status = proxy_task(id)
    if status > 2:
        return HttpResponse('error')
    return HttpResponse('ok')

def json_response(func):
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        try:
            data = json.dumps(objects)
            if 'jsonpCallback' in request.REQUEST:
                data = '%s(%s);' % (request.REQUEST['jsonpCallback'], data)
                return HttpResponse(data, "text/javascript")
        except:
            data = json.dumps(str(objects))
        return HttpResponse(data, "application/json")
    return decorator

def json_response(func):
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        try:
            data = json.dumps(objects)
            if 'jsonpCallback' in request.REQUEST:
                data = '%s(%s);' % (request.REQUEST['jsonpCallback'], data)
                return HttpResponse(data, "text/javascript")
        except:
            data = json.dumps(str(objects))
        return HttpResponse(data, "application/json")
    return decorator

def html_to_json(html):
    the_data = {'status':'200', 'title':html.title, 'tags':html.tags, 'desc':html.summerize\
            ,'classify':html.classify, 'content':TextToHtml(html.content), 'results': html.preview}
    return the_data

@json_response
def proxy_to(request, path):
    # Use escape in javascript
    url = request.GET.get('url')
    if not url or not url.lower().startswith('http'):
        return {'status':'500'}
    url = url.lower()
    try:
        html = HtmlContent.objects.get(url=url)
    except:
        html = HtmlContent(url=url, status=2, hash=0)
        html.save()

        #job = default_queue.enqueue(proxy_task, html.id)
        #add_task('default', '%s/task/%d' % (BASE_URL, html.id))
        redis_queue(url)

        # wait for processing
        #print 'wait for processing'
        return {'status':'202'}
    if html.status > 2:
        #print 'processed but error in processing'
        # processed but error in processing
        return {'status':'500'}
    elif html.content != '':
        # prcessed ok
        #print 'ok'
        return html_to_json(html)
    else:
        #job = default_queue.enqueue(proxy_task, html.id)
        #redis_queue(url)
        return {'status':'202'}

class NewsListView(ListView):
    queryset = HtmlContent.objects.filter(status=0).filter(~Q(content='')).order_by('-id')
    paginate_by = 25
    template_name = 'news_list.html'

def NewsSubject(request, id):
    try:
        obj = HtmlContent.objects.get(pk=id)
        return render_to_response('news_subject.html', {'entry':obj})
    except:
        return HttpResponse('No find!')

def like_models(request, path):
    # Use escape in javascript
    url = request.GET.get('url')
    try:
        html = HtmlContent.objects.get(url=url)
    except:
        return HttpResponse("No find!")
    object_list = sim_search(html)
    return render_to_response('sim_list.html', {'object_list':object_list})

def unescape(c):
    #return "".join([(len(i)>0 and unichr(int(i,16)) or "") for i in c.split('%u')])
    return c.replace('%','\\').decode('unicode-escape')

def search_content(request, path):
    # Use escape in javascript
    content = request.GET.get('s')
    if content and content.strip() != '':
        content = unescape(content)
        object_list = sim_content(content)
    else:
        object_list = None
        content = ''
    return render_to_response('search.html', {'content':content,'object_list':object_list})

def test_page(request):
    return render_to_response('test.html')

class DupListView(ListView):
    queryset = HtmlContent.objects.filter(status=1).filter(~Q(content='')).order_by('-id')
    paginate_by = 25
    template_name = 'dup_list.html'

class ClassShow(ListView):
    template_name = 'cls_list.html'
    paginate_by = 25
    #model = HtmlContent

    def get_queryset(self):
        print self.kwargs
        id = self.kwargs['id']
        cls = id2cls_func(int(id))
        object_list = HtmlContent.objects.filter(status=1).filter(classify=cls).filter(~Q(content='')).order_by('-id')
        return object_list

    def get_context_data(self, **kwargs):
        context = super(ClassShow, self).get_context_data(**kwargs)
        id = self.kwargs['id']
        cls = id2cls_func(int(id))
        context['classify'] = cls
        context['the_ids'] = range(10)
        return context
