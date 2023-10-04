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
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
import time



class diarioCrawler(scrapy.Spider):
    name = "diarioCrawler"
    allowed_domains = ["eldiariodechihuahua.mx", "eldiariodedelicias.mx", "eldiariodeparral.mx"]
    start_urls = ["https://www.eldiariodechihuahua.mx"]
    stop_crawling = False

    custom_settings = {
        'FEED_URI': 'DiarioChihuahua.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'DEPTH_LIMIT': 100000,
        'CONCURRENT_REQUESTS': 20,
        'MEMUSAGE_NOTIFY_MAIL': ['luis3.14xbox@live.com'],
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.3'
    }

    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def parse(self, response):
        section_urls = response.css("div.rcx12.menu > div.site-name a::attr(href)").getall()
        for section in section_urls:
            if ((section  != "https://www.eldiariodechihuahua.mx/seccion/Opinion/") and (section != "https://www.eldiariodechihuahua.mx/clasificado/") and (section != "https://www.eldiariodechihuahua.mx/")):
                yield response.follow(section, callback = self.parse_page)

    def parse_item(self, response):

        diario = DiarioChiItems()
        diario["URL"] = response.url
        diario["title"] = response.css("h1::text").extract_first()
        diario["subtitle"] = response.css('div[class*="rcx12"] > p::text').extract_first()
        diario["section"] = response.css("div.rcx12 > small::text").get()
        diario["date"] = response.css('div[class*="rcx9"] div.rcx12 > small::text').get()
        diario["place"] = response.css("strong em::text").get()
        diario["body"] = response.css('.rcx12#cuerpo_nota >p::text').extract()
        diario["img_link"] = response.css("figure > amp-img::attr(src)").get()
        
        target_date = "01 julio 2022" 
        raw_date = response.css('div[class*="rcx9"] div.rcx12 > small::text').get()
        if target_date in raw_date:
            self.stop_crawling = True

        if not self.stop_crawling:
            yield diario


    def parse_page(self, response):
        if not self.stop_crawling:
            self.driver.get(response.url)
            n = 0 # Number of clicks in the button
            limit = 10000000 # Limit of number of clicks
            sel = None
            try:
                while n < limit and not self.stop_crawling:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    next_button = self.driver.find_element(By.XPATH, '//button[text()="Ver más"]')
                    next_button.click()
                    self.log('Clicked on "Ver más" button.')
                    wait = WebDriverWait(self.driver, 10)
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Ver más"]')))
                    sel = Selector(text=self.driver.page_source)
                    n += 1
            except NoSuchElementException:
                self.log('No more pages to load.')

            if sel and not self.stop_crawling:
                links = sel.css("article a ::attr(href)").getall()
                for link in links:
                    yield response.follow(url=link, callback=self.parse_item)

            self.driver.quit()