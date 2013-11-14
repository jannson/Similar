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
#import simplejson as json
import json
import urllib2

from django.db.models import Q

from settings import *
from pull.models import *
from extract import TextExtract, TextToHtml, ContentEncodingProcessor, USER_AGENT

if not sae_debug:
    import sae.mail
    from sae.taskqueue import add_task
    from sae.storage import Bucket

html_remove = re.compile(r'\s*<.*?>\s*',re.I|re.U|re.S)
re_head = re.compile(r'<[head^>]*>.*</head>', re.I|re.U|re.S)
re_keywords = re.compile(r'<meta\s+name=[\'"]keywords[\'"]\s+content\s*=\s*[\'"]([^\'"]+)[\'"][^>]*>', re.I|re.U|re.S)
re_desc = re.compile(r'<meta\s+name=[\'"]description[\'"]\s+content\s*=\s*[\'"]([^\'"]+)[\'"][^>]*>', re.I|re.U|re.S)
#USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5'

def task_to(request, id):
    try:
        html = HtmlContent.objects.get(pk=id)
        #print 'html content', html.content
        if html.retry != 3 and html.content != '':
            return HttpResponse('ok')
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
        html.retry = 3
        print 'urllib2 error'
    else:
        try:
            ucontent = content.decode('utf-8')
        except UnicodeDecodeError:
            ucontent = content.decode('gbk','ignore')
        head = re_head.search(ucontent)
        if head:
            head_str = head.group()
            keywords = re_keywords.search(head_str)
            if keywords:
                html.tags = keywords.group(1)
            else:
                html.tags = ''
            desc = re_desc.search(head_str)
            if desc:
                html.summerize = desc.group(1)[0:150]
            else:
                html.summerize = ''
        #print 'parsing'
        tx = TextExtract(ucontent)
        #print 'parsed'
        html.title = tx.title
        html.content = tx.content.strip()
        if tx.content == '':
            print 'Parse html error'
            html.retry = 3
        else:
            s_len = len(html.summerize)
            html.summerize += html.content[s_len:(150-s_len)].replace('\n','')
            if len(html_remove.sub('', tx.preview)) < 250:
                html.preview = TextToHtml(tx.content)
            else:
                html.preview = tx.preview

    #print html.id, html.title, html.tags, html.summerize
    html.save()
    if html.retry == 3:
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
    the_data = {'status':'200', 'title':html.title, 'tags':html.tags, 'desc':html.summerize, 'results': html.preview}
    return the_data

@json_response
def proxy_to(request, path):
    # Use escape in javascript
    url = request.GET.get('url')
    try:
        html = HtmlContent.objects.get(url=url)
    except:
        html = HtmlContent(url=url, retry=0)
        html.save()
        add_task('default', '%s/task/%d' % (BASE_URL, html.id))
        # wait for processing
        #print 'wait for processing'
        return {'status':'202'}
    if html.retry == 3:
        #print 'processed but error in processing'
        # processed but error in processing
        return {'status':'500'}
    elif html.content != '':
        # prcessed ok
        #print 'ok'
        return html_to_json(html)
    else:
        return {'status':'202'}

class NewsListView(ListView):
    queryset = HtmlContent.objects.filter(~Q(retry=3)).filter(~Q(content='')).order_by('-id')
    paginate_by = 25
    template_name = 'news_list.html'

def NewsSubject(request, id):
    try:
        obj = HtmlContent.objects.get(pk=id)
        return render_to_response('news_subject.html', {'entry':obj})
    except:
        return HttpResponse('No find!')
