# from scrapy import Spider
import scrapy
import re
import json


class CitrusSpider(scrapy.Spider):
    name = 'ctrs'
    allowed_domains = ["api.ctrs.com.ua"]
    
    category = 'noutbuki-i-ultrabuki'
    last_page = 2

    page = [item for item in range(1, last_page + 1)]
    start_urls = [f'https://api.ctrs.com.ua/router?with_meta=1&l=uk&url=/{category}/page_1/']

    def start_requests(self):
        for number in self.page:
            url = f'https://api.ctrs.com.ua/router?with_meta=1&l=uk&url=/{self.category}/page_{number}/'
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        req = json.loads(response.text) 
        data = req["data"]
        facetObject = data["facetObject"]
        items = facetObject["items"]
        
        for item in items:
            if item['preview']['src'].endswith('.webp'):
                yield {
                    "id": item['id'],
                    "url": item['url'],
                    "src": item['preview']['src']
                }
        
        # Поиск и переход по другим ссылкам на сайте
        # if facetObject['pages']['nextPage']:
        #     page += 1
        #     yield response.follow(next_page, self.parse)
