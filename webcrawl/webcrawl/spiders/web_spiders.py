# -*- coding: utf-8 -*

import re
from scrapy import log
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from webcrawl.items import WebcrawlItem
import urlparse
from scrapy.utils.url import urljoin_rfc

import extract as tex

html_remove = re.compile(r'\s*<.*?>\s*',re.I|re.U|re.S)

class MovieSpider(CrawlSpider):
    name = 'web_crawl'
    allowed_domains = ['alibuybuy.com']
    start_urls = ['http://www.alibuybuy.com/tag/%E4%BA%A7%E5%93%81%E5%B8%82%E5%9C%BA']

    rules = (
        Rule(SgmlLinkExtractor(allow=r'/tag/(.+)', ), follow=True),
        Rule(SgmlLinkExtractor(allow=r'/posts/\d+\.html$'), callback='parse_web_content'),
    )

    def parse_web_content(self, response):
        #log.msg('####title='+response.body, level=log.ERROR)

        url = response.url
        if url[0:4] != 'http':
            url = 'http://www.alibuybuy.com'+url

        item = WebcrawlItem()
        item['retry'] = 3
        item['url'] = url

        tx = tex.TextExtract(response.body)
        item['title'] = tx.title
        item['content'] = tx.content.strip()
        if tx.content != '':
            item['retry'] = 0
            if len(html_remove.sub('', tx.preview)) < 250:
                item['preview'] = TextToHtml(tx.content)
            else:
                item['preview'] = tx.preview
        return item
