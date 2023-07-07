from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class diarioCrawler(CrawlSpider):
    name = "diarioCrawler"
    allowe_domains = ["eldiariodechihuahua.mx/"]
    start_urls = ["https://www.eldiariodechihuahua.mx/seccion/Local/"]


    rule  = (
        Rule(LinkExtractor(allow = "local")),
    )


    