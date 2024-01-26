import scrapy
from newscrawler.items import DiarioChiItems
from scrapy.selector import Selector

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
        'DEPTH_LIMIT': 100000,
        'CONCURRENT_REQUESTS': 20,
        'MEMUSAGE_NOTIFY_MAIL': ['luis3.14xbox@live.com'],
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.3'
    }

    def parse(self, response):
        section_urls = response.css("div.rcx12.menu > div.site-name a::attr(href)").getall()
        for section in section_urls:
            if section not in ["https://www.eldiariodechihuahua.mx/seccion/Opinion/", 
                               "https://www.eldiariodechihuahua.mx/clasificado/",
                               "https://www.eldiariodechihuahua.mx/",
                               "https://eldiariodeparral.mx/seccion/Sociales/",
                               "https://eldiariodedelicias.mx/seccion/Sociales/"]:
                yield response.follow(section, callback = self.parse_page)

    def parse_page(self, response):
        if not self.stop_crawling:
            page_num = 0  # Starting page
            section_name = response.url.split('/')[-2]  # Extracting section name from the url

            # Determine the base domain
            base_domain = response.url.split('/')[2]
            print(f"Base_domain: {base_domain}")
            # Use the base domain to construct the AJAX request URL
            next_url = f"https://{base_domain}/app_config/scroll.php?page={page_num}&cabeza={section_name}"

            yield scrapy.Request(next_url, callback=self.parse_scroll_content, meta={'page_num': page_num, 'section_name': section_name, 'base_response': response, 'base_domain': base_domain})


    def parse_scroll_content(self, response):
        try:
            # Intenta cargar la respuesta como JSON
            data = json.loads(response.text)
            # Aquí puedes extraer los datos específicos del JSON, por ahora simplemente lo imprimiré
            # para que sepas que tienes que procesar este JSON:
            #print(data)
            # Dependiendo de la estructura del JSON, tendrías que extraer los enlaces y otros datos relevantes
            # Por ejemplo:
            # links = [item['url'] for item in data['items']]
        except json.JSONDecodeError:
            # Si no es JSON, trata la respuesta como HTML
            sel = Selector(text=response.text)
            links = sel.css("article a ::attr(href)").getall()
            for link in links:
                yield response.follow(url=link, callback=self.parse_item)

        # Check if there's more to scroll
        if not self.stop_crawling and "content indicating no more data" not in response.text:
            page_num = response.meta['page_num'] + 1
            section_name = response.meta['section_name']

            # Use the base domain from meta to construct the AJAX request URL
            base_domain = response.meta['base_domain']
            next_url = f"https://{base_domain}/app_config/scroll.php?page={page_num}&cabeza={section_name}"

            yield scrapy.Request(next_url, callback=self.parse_scroll_content, meta={'page_num': page_num, 'section_name': section_name, 'base_response': response, 'base_domain': base_domain})

    def parse_item(self, response):

        diario = DiarioChiItems()
        diario["URL"] = response.url
        diario["title"] = response.css("h1::text").extract_first()
        diario["subtitle"] = response.css('div[class*="rcx12"] > p::text').extract_first()
        diario["section"] = response.css("div.rcx12 > small::text").get()
        diario["date"] = response.css('div[class*="rcx9"] div.rcx12 > small::text').get()
        diario["place"] = response.css("strong em::text").get()
        #diario["body"] = response.css('.rcx12#cuerpo_nota >p::text').extract()
        diario["body"] = '\n'.join(response.css('.rcx12#cuerpo_nota >p::text').getall())
        diario["img_link"] = response.css("figure > amp-img::attr(src)").get()
        
        target_date = "01 julio 2022" 
        raw_date = response.css('div[class*="rcx9"] div.rcx12 > small::text').get()
        if target_date in raw_date:
            self.stop_crawling = True

        if not self.stop_crawling:
            yield diario
