import scrapy
import logging

class MySpider(scrapy.Spider):
    name = "myspider"
    allowed_domains = ["dirlt.com"]
    start_urls = ["http://dirlt.com/index.html"]
    logger = logging.getLogger('MySpider')

    def Open(self):
        print 'open myspider'
        self.fh = open('output.log', 'w')

    def Close(self):
        print 'close myspider'
        self.fh.close()

    def parse(self, response):
        urls = response.xpath('//a/@href').extract()
        images = response.xpath('//img/@src').extract()
        links = urls + images
        links = filter(lambda x: not x[0].startswith('#'), links)
        for link in links:
            url = response.urljoin(link)
            try:
                self.fh.write(url + '\n')
            except:
                # probably encoding problem.
                self.logger.warning('failed to write ' + url)
            if url.endswith('.html'):
                yield scrapy.Request(url)
