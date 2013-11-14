# Scrapy settings for webcrawl project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import sys, os, os.path

reload(sys) 
sys.setdefaultencoding('utf-8')

BOT_NAME = 'webcrawl'

SPIDER_MODULES = ['webcrawl.spiders']
NEWSPIDER_MODULE = 'webcrawl.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'webcrawl (+http://www.yourdomain.com)'

DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'douban (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5'

ITEM_PIPELINES = [
    'scrapy.contrib.pipeline.images.ImagesPipeline',
    'webcrawl.pipelines.WebcrawlPipeline',
]

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES_STORE = os.path.join(HERE, '..', 'covers')

dj_path = os.path.join(HERE,'..','..')
sys.path.insert(13, dj_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pull.settings'
