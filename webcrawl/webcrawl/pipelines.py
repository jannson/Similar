# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys, os, os.path
from scrapy import log
from scrapy.exceptions import DropItem

from django.contrib.auth.models import User
from pull.models import *

class WebcrawlPipeline(object):
    def process_item(self, item, spider):
        
        if item['retry'] == 3:
            raise DropItem('error processing html')

        url = item['url']
        try:
            html = HtmlContent.objects.get(url=url)
        except:
            html = HtmlContent(url=url, retry=0)

        html.url = url
        html.title = item['title']
        html.retry = item['retry']
        html.content = item['content']
        html.preview = item['preview']
        html.summerize = ''
        html.tags = ''
        html.save()
