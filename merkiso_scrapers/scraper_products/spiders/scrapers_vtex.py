import traceback
from typing import Final, List
import scrapy

from string import Template
from scrapy.crawler import CrawlerProcess
from scraper_products.db.database import DbThreadConnection
from scraper_products.db.models.stores import Store
from scraper_products.items import ProductListItem, ProductItem
from scraper_products.utils.build_url import build_url
from itemloaders import ItemLoader


class ScrapersVtex(scrapy.Spider):
    name = "scrapers_vtex"
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

    handle_httpstatus_list = [406]


    def get_stores(self):
        db_thread_connection = DbThreadConnection(pool_size = 10, max_overflow = 15, pool_recycle = -1)
        with db_thread_connection.session() as db_session:
            stores = db_session.query(Store).all()
            return stores
    
    def __init__(self, product_name: str, **kwargs):
        self.search_data = {
            "search_name": product_name,
            "stores": [store.__json__() for store in self.get_stores()],
        }
        super(ScrapersVtex, self).__init__(**kwargs)


    def start_requests(self):
        for store in self.search_data['stores']:

            query_param_products = {
                "query": self.search_data['search_name']
            }
            
            domain = store.get("domain")

            URL_PRODUCTS = self.URL_PRODUCTS_TEMPLATE.substitute(domain=domain)
            
            url = build_url(URL_PRODUCTS, query_param_products)

            yield scrapy.Request(
                url=url,
                method="GET",
                callback=self.parse,
                meta={"store": store}
            )

    def parse(self, response):
        try:
            store = response.meta["store"]
            
            response_json = response.json()
            products = response_json["products"]
            product_items = []
            
            item_loader = ItemLoader(item=ProductListItem())
            item_loader.add_value("search_data", self.search_data)
            
            for product in products:
                products_items = product.get("items", [])
                
                for product_item in products_items:
                    price = 0

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
                        "search_name" : self.search_data["search_name"],
                        "product_id": product_item["itemId"],
                        "name": product_item["name"],
                        "description": product_item["complementName"],
                        "url": product["link"],
                        "ean": product_item["ean"],
                        "sku": '',
                        "availability": availability,
                        "price": price,
                        "images": [image['imageUrl'] for image in product_item["images"] if image['imageUrl']],
                        "store": store
                    }

                    product_items.append(self.create_item_product(product_data))
                
            item_loader.add_value("products", product_items)
            
            yield item_loader.load_item()
        except Exception as e:
            traceback.print_exc()
            yield {"error": True}

    def create_item_product(self, product_data):

        item_loader = ItemLoader(item=ProductItem())
        
        for key, value in product_data.items():
            item_loader.add_value(key, value)

        return item_loader.load_item()

    

if __name__ == "__main__":

    # Instancia el spider
    mi_spider_instance = ScrapersVtex

    # Configura y ejecuta el proceso de Scrapy
    process = CrawlerProcess()
    process.crawl(
        mi_spider_instance, 
        product_name="manzana"
    )
    process.start()
