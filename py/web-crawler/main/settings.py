# Scrapy settings for main project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

#BOT_NAME = 'main'
#BOT_VERSION = '1.0'

SPIDER_MODULES = ['main.spiders']
NEWSPIDER_MODULE = 'main.spiders'
#USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
DOWNLOAD_TIMEOUT = 1

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'

DOWNLOAD_HANDLERS = {
    's3': None
}
LOG_FILE = "scrapy.log"

ITEM_PIPELINES = {
    'main.pipelines.MainPipeline': 300,
}
