import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from scrapy.selector import Selector
from scrapy.http import Request
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from newscrawler.items import DiarioChiItems
from selenium.webdriver.support.expected_conditions import staleness_of

class diarioCrawler(scrapy.Spider):
    name = "diarioCrawler"
    allowed_domains = ["eldiariodechihuahua.mx"]
    start_urls = ["https://www.eldiariodechihuahua.mx/seccion/Local/"]

    custom_settings = {
        'FEED_URI': 'DiarioChihuahua.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'DEPTH_LIMIT': 20,
        'CONCURRENT_REQUESTS': 70,
        'MEMUSAGE_NOTIFY_MAIL': ['luis3.14xbox@live.com'],
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.3'
    }

    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def parse(self, response):
        self.driver.get(response.url)
        n = 0 # Number of clicks in the button
        limit = 5 # Limit of number of clicks
        sel = None
        try:
            while n < limit:
                old_page = self.driver.find_element(By.TAG_NAME, 'html')
                next_button = self.driver.find_element(By.XPATH, '//button[text()="Ver más"]')
                next_button.click()
                self.log('Clicked on "Ver más" button.')
                WebDriverWait(self.driver, 10).until(staleness_of(old_page))
                sel = Selector(text=self.driver.page_source)
                n += 1
        except NoSuchElementException:
            self.log('No more pages to load.')

        self.log(f'The limit of pages has been reached. {n} pages reached.')
        if sel:
            links = sel.css("article a ::attr(href)").getall()
            print("========================================")
            print("========================================")
            print(links)
            print("========================================")
            print("========================================")

            for link in links:
                self.log(link)
                yield Request(url=link, callback=self.parse_item)

        self.driver.quit()

    def parse_item(self, response):
        print("")
        print("")
        print("Item parse")
        print("")
        print("")
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
