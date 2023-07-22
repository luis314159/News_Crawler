# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewscrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class DiarioChiItems(scrapy.Item):
        
        URL = scrapy.Field()
        title = scrapy.Field()
        subtitle = scrapy.Field()
        section = scrapy.Field()
        place = scrapy.Field()
        date = scrapy.Field()
        body = scrapy.Field()
        img_link = scrapy.Field()

        
