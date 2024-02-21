
import json
from typing import Final
import scrapy

from string import Template
from scrapy.crawler import CrawlerProcess
from scrapers_searchs.utils.build_url import build_url

from scrapers_searchs.structs.items_car_shop import BuildItems



class BuildCarShopingVtex(scrapy.Spider):
    name = "build_car_shopping_vtex"
    allowed_domains = ["www.olimpica.com"]
    
    URL_CHECKOUT: Final[str] = Template('https://$domain/api/checkout')
    PATH_CREATE_CAR_SHOPPING: Final[str] = "/pub/orderForm"
    QUERY_PARAM_CREATE_CAR_SHOPPING: Final[dict] = {
        "forceNewCart": 'true',
    }
    QUERY_PARAM_CREATE_ITEMS_CAR_SHOPPING: Final[dict] = {
        "allowedOutdatedData": "paymentData",
    }

    def __init__(self, domain: str ,data: dict, **kwargs):
        self.build_items = BuildItems.model_validate(data)
        self.URL_CHECKOUT = self.URL_CHECKOUT.substitute(domain=domain)
        super(BuildCarShopingVtex, self).__init__(**kwargs)

    def start_requests(self):

        url = f"{self.URL_CHECKOUT}{self.PATH_CREATE_CAR_SHOPPING}"
        url = build_url(url, self.QUERY_PARAM_CREATE_CAR_SHOPPING)
        
        yield scrapy.Request(
            url=url,
            method="GET",
            callback=self.post_save_items,
        )

    
    def post_save_items(self, response):

        response_json = response.json()
        order_form_id = response_json["orderFormId"]

        url = f"{self.URL_CHECKOUT}{self.PATH_CREATE_CAR_SHOPPING}/{order_form_id}/items"
        url = build_url(url, self.QUERY_PARAM_CREATE_ITEMS_CAR_SHOPPING)

        yield scrapy.Request(
            url=url,
            method="POST",
            body=json.dumps(self.build_items.model_dump()),
            callback=self.parse,
            meta={"order_form_id": order_form_id},
        )

    def parse(self, response):

        order_form_id_param = {
            "orderFormId": response.meta["order_form_id"]
        }
        
        self.URL_CHECKOUT_FINAL = build_url(self.URL_CHECKOUT.replace('/api', ''), order_form_id_param)
        print(F"URL_CHECKOUT_FINAL {self.URL_CHECKOUT_FINAL}")
    

if __name__ == "__main__":

    # Instancia el spider
    mi_spider_instance = BuildCarShopingVtex

    # Configura y ejecuta el proceso de Scrapy
    process = CrawlerProcess()
    process.crawl(mi_spider_instance, data={
            "orderItems": [
                {
                    "quantity": 3,
                    "seller": "1",
                    "id": "176910",
                    "index": 0
                },
                {
                    "quantity": 1,
                    "seller": "1",
                    "id": "776582",
                    "index": 0
                },
            ]
        },
        domain="www.olimpica.com")
    process.start()
