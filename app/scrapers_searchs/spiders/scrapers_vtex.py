from typing import Final
import scrapy

from string import Template
from scrapy.crawler import CrawlerProcess
from scrapers_searchs.items import ProductListItem, ProductItem
from scrapers_searchs.utils.build_url import build_url
from itemloaders import ItemLoader


class ScraperVtex(scrapy.Spider):
    name = "scraper_vtex"
    allowed_domains = ["*"]


    URL_PRODUCTS_TEMPLATE: Final[str] = Template('https://$domain/api/io/_v/api/intelligent-search/product_search')
    COUNT_PRODUCTS_PER_PAGE: Final[int] = 10
    
    QUERY_PARAM_PRODUCTS: Final[dict] = {
        "query": "product_name",
        "hideUnavailableItems": "true",
        "sort": "price:asc",
        "count": COUNT_PRODUCTS_PER_PAGE
    }

    STORE: str = "store"
    
    def __init__(self, domain: str , store: str, product_name: str, **kwargs):
        self.URL_PRODUCTS = self.URL_PRODUCTS_TEMPLATE.substitute(domain=domain)
        self.QUERY_PARAM_PRODUCTS["query"] = product_name
        self.STORE = store
        super(ScraperVtex, self).__init__(**kwargs)

    def start_requests(self):
        url = build_url(self.URL_PRODUCTS, self.QUERY_PARAM_PRODUCTS)

        yield scrapy.Request(
            url=url,
            method="GET",
            callback=self.parse,
        )

    
    def parse(self, response):

        response_json = response.json()
        products = response_json["products"]

        product_items = []
        
        item_loader = ItemLoader(item=ProductListItem())
        
        for product in products:
            products_items = product.get("items", [])
            
            for product_item in products_items:
                price = 0
                availability = False
                comercial_offer = {}
                
                sellers = list(
                    filter(
                        lambda x: x["sellerDefault"] == True,
                        product_item["sellers"]
                    )
                )
                
                if sellers:
                    comercial_offer = sellers[0]["commertialOffer"]
                    
                if comercial_offer:
                    availability = comercial_offer["AvailableQuantity"] > 0
                    price = comercial_offer["Price"]
                
                product_data = {
                    "name": product_item["name"],
                    "description": product_item["complementName"],
                    "url": product["link"],
                    "ean": product_item["ean"],
                    "sku": '',
                    "availability": availability,
                    "price": price,
                    "images": [image['imageUrl'] for image in product_item["images"] if image['imageUrl']],
                    "store": self.STORE
                }

                product_items.append(self.create_item_product(product_data))
            
        item_loader.add_value("products", product_items)
        
        yield item_loader.load_item()

    def create_item_product(self, product_data):

        item_loader = ItemLoader(item=ProductItem())
        
        for key, value in product_data.items():
            item_loader.add_value(key, value)

        return item_loader.load_item()

    

if __name__ == "__main__":

    # Instancia el spider
    mi_spider_instance = ScraperVtex

    # Configura y ejecuta el proceso de Scrapy
    process = CrawlerProcess()
    process.crawl(
        mi_spider_instance, 
        domain="www.olimpica.com",
        store='olimpica',
        product_name="detergente liquido"
    )
    process.start()
