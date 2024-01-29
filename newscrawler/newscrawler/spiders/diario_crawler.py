import scrapy
from newscrawler.items import DiarioChiItems
from scrapy.selector import Selector
import logging

import json

class diarioCrawler(scrapy.Spider):
    name = "diarioCrawler"
    allowed_domains = ["eldiariodechihuahua.mx", "eldiariodedelicias.mx", "eldiariodeparral.mx"]
    start_urls = ["https://www.eldiariodechihuahua.mx"]#, "https://eldiariodedelicias.mx/", "https://eldiariodeparral.mx/"]
    stop_crawling = False

    custom_settings = {
        'FEED_URI': 'DiarioChihuahua2.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'DEPTH_LIMIT': 10,
        'CONCURRENT_REQUESTS': 20,
        'MEMUSAGE_NOTIFY_MAIL': ['luis3.14xbox@gmail.com'],
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.3'
    }

    def parse(self, response):
        logging.info("Parse function called on URL: " + response.url)
        section_urls = response.css("div.rcx12.menu > div.site-name a::attr(href)").getall()
        for section in section_urls:
            if section not in ["https://www.eldiariodechihuahua.mx/seccion/Opinion/", 
                               "https://www.eldiariodechihuahua.mx/clasificado/",
                               "https://www.eldiariodechihuahua.mx/",
                               "https://eldiariodeparral.mx/seccion/Sociales/",
                               "https://eldiariodedelicias.mx/seccion/Sociales/"]:
                yield response.follow(section, callback = self.parse_page)

    def parse_page(self, response):
        logging.info("Parse page called on URL: " + response.url)
        if not self.stop_crawling:
            page_num = 0  # Starting page
            section_name = response.url.split('/')[-2]  # Extracting section name from the url

            # Determine the base domain
            base_domain = response.url.split('/')[2]
            #print(f"Base_domain: {base_domain}")
            # Use the base domain to construct the AJAX request URL
            next_url = f"https://{base_domain}/app_config/scroll.php?page={page_num}&cabeza={section_name}"

            yield scrapy.Request(next_url, callback=self.parse_scroll_content, meta={'page_num': page_num, 'section_name': section_name, 'base_response': response, 'base_domain': base_domain})


    def parse_scroll_content(self, response):
        logging.info("Parse scroll content called on URL: " + response.url)
        try:
            # Intenta cargar la respuesta como JSON
            data = json.loads(response.text)
            # Aquí puedes extraer los datos específicos del JSON, por ahora simplemente lo imprimiré
            # para que sepas que tienes que procesar este JSON:
            #print(data)
            # Dependiendo de la estructura del JSON, tendrías que extraer los enlaces y otros datos relevantes
            # Por ejemplo:
            # links = [item['url'] for item in data['items']]
            if data[0] == False:
                #raise Exception("No json files")
                logging.info("No Json files")
            else: 
                #logging.info("json files :" + str(data))

                base_url = response.url.split('/')[2]  # Asumiendo que este es el dominio base
                #links = [base_url + '/' + item for item in data[0].get('url')]
                links = [base_url + '/' + item['url'] for item in data if 'url' in item if len(item['url'])> 4]
                logging.info(f"links: {links}")
                # Procesa cada enlace encontrado en el JSON
                for link in links:

                    logging.info("Gonna try:" + str(link))
                    yield response.follow(url=link, callback= self.parse_item)

        except json.JSONDecodeError:
            # Si no es JSON, trata la respuesta como HTML
            sel = Selector(text=response.text)
            links = sel.css("article a ::attr(href)").getall()
            logging.info("URLS finded: " + links)
            for link in links:
                yield response.follow(url=link, callback = self.parse_item)

        # Check if there's more to scroll
        if not self.stop_crawling and "content indicating no more data" not in response.text:
            page_num = response.meta['page_num'] + 1
            section_name = response.meta['section_name']

            # Use the base domain from meta to construct the AJAX request URL
            base_domain = response.meta['base_domain']
            next_url = f"https://{base_domain}/app_config/scroll.php?page={page_num}&cabeza={section_name}"

            yield scrapy.Request(next_url, callback=self.parse_scroll_content, meta={'page_num': page_num, 'section_name': section_name, 'base_response': response, 'base_domain': base_domain})

    def parse_item(self, response):
        logging.info("Parse item called on URL: " + response.url)
        diario = DiarioChiItems()
        diario["URL"] = response.url
        diario["title"] = response.css("h1::text").extract_first()
        title = response.css("h1::text").extract_first()
        logging.info(f"Title extracted: {title}")
        diario["subtitle"] = response.xpath("//div[@class='rcx12 pading_0']/following-sibling::p[1]/text()").get()
        diario["section"] = response.css("div.rcx12 > small::text").get()
        diario["date"] = response.css('div[class*="rcx9"] div.rcx12 > small::text').get()
        diario["place"] = response.css("strong em::text").get()
        #diario["body"] = response.css('.rcx12#cuerpo_nota >p::text').extract()
        diario["body"] = '\n'.join(response.css('.rcx12#cuerpo_nota >p::text').getall())
        diario["img_link"] = response.css("figure > amp-img::attr(src)").get()
        
        target_date = "01 julio 2022" 
        raw_date = response.css('div[class*="rcx9"] div.rcx12 > small::text').get()
        yield diario
        self.stop_crawling = True

        if target_date in raw_date:
            self.stop_crawling = True

        if not self.stop_crawling:
            yield diario
