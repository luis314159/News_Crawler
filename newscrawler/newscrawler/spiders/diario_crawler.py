from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request


class diarioCrawler(CrawlSpider):
    name = "diarioCrawler"
    allowe_domains = ["eldiariodechihuahua.mx/"]
    start_urls = ["https://www.eldiariodechihuahua.mx/"]


    rule  = (
        Rule(LinkExtractor(allow = "seccion"),callback = "parse_item"),
    )

    def parse_item(self, response):
        next_page_links = response.xpath('//xpath[to_links]').getall()
        for link in next_page_links:
            yield Request(response.urljoin(link), callback=self.parse_item # o otro callback
                          )
