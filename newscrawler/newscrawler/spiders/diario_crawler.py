from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from newscrawler.items import DiarioChiItems
import logging

class diarioCrawler(CrawlSpider):
    name = "diarioCrawler"
    allowed_domains = ["eldiariodechihuahua.mx"]
    start_urls = ["https://www.eldiariodechihuahua.mx/"]

    custom_settings = {
        'FEED_URI': 'DiarioChihuahua.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'DEPTH_LIMIT': 20,
        'CONCURRENT_REQUEST': 24,
        'MEMUSAGE_NOTIFY_MAIL': ['luis3.14xbox@live.com'],
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.3'
        }

    rules  = (
        Rule(LinkExtractor(allow = r"seccion/local"), callback = "parse_item"),
    )

    def parse_start_url(self, response):
        links = response.css("article a ::attr(href)").getall()
        logging.info("======================")
        logging.info(len(links))
        logging.info("======================")
        for link in links:
            yield response.follow(link, callback = self.parse_item)

    def parse_item(self, response ):
        diario = DiarioChiItems()
        diario["URL"] = response.url
        diario["title"] = response.css("h1::text").extract_first()
        diario["subtitle"] = response.css('div[class*="rcx12"] > p::text').extract_first()
        diario["section"] = response.css("div.rcx12 > small::text").get()
        diario["date"] = response.css('div[class*="rcx9"] div.rcx12 > small::text').get()
        diario["place"] = response.css("strong em::text").get()
        diario["body"] = response.css('.rcx12#cuerpo_nota >p::text').extract()
        diario["img_link"] = response.css("figure > amp-img::attr(src)").get()

        yield diario

        
