# lib
import base64
import json
from scrapy.crawler import CrawlerProcess
from itemloaders import ItemLoader
from string import Template
from typing import Final
import traceback
import scrapy

# app
from scraper_products.items import ProductListItem, ProductItem
from scraper_products.utils.build_url import build_url
from scraper_products.db.database import DbConnection
from scraper_products.constants import COLLECTIONS
from scraper_products.settings import MONGO_DB
from bson.objectid import ObjectId

class ScrapersVtex(scrapy.Spider):
    name = "scrapers_vtex"
    allowed_domains = []

    URL_PRODUCTS_TEMPLATE: Final[str] = Template('https://$domain/api/io/_v/api/intelligent-search/product_search')
    COUNT_PRODUCTS_PER_PAGE: Final[int] = 10
    
    QUERY_PARAM_PRODUCTS: Final[dict] = {
        "query": "product_name",
        "hideUnavailableItems": "true",
        "sort": "price:asc",
    }

    STORE: str = "store"

    handle_httpstatus_list = [406]

    def get_stores(
        self,
        ids: str,
    ):  

        db_connection = DbConnection()
        stores = list(db_connection.find(
            db_name=MONGO_DB,
            collection_name=COLLECTIONS['stores'],
            query={}
        ))

        if ids:

            #decode ids from base64
            decode_ids_b64 = base64.b64decode(ids)
            decode_ids_b64 = decode_ids_b64.decode('utf-8')
            decode_ids_b64 = json.loads(decode_ids_b64)
            ids = [ObjectId(_id) for _id in decode_ids_b64]
            
            stores_sucursals = list(db_connection.find(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['sucursals'],
                query={
                    "_id": {"$in": ids}
                }
            ))
            
            if stores_sucursals:
                for store in stores:
                    store_sucursal = list(
                        filter(
                            lambda x: x["store"]["_id"] == store["_id"],
                            stores_sucursals
                        )
                    )
                    
                    if store_sucursal:
                        store_sucursal = store_sucursal[0]
                        store["near_sucursal"] = store_sucursal

        return stores


    def __init__(self, product_name: str, **kwargs):
        
        sucursal_ids = kwargs.get("sucursal_ids")
        
        self.search_data = {
            "search_name": product_name,
            "stores": [store for store in self.get_stores(sucursal_ids)],
        }
        super(ScrapersVtex, self).__init__(**kwargs)


    def start_requests(self):

        for store in self.search_data['stores']:

            query_param_products = {
                **self.QUERY_PARAM_PRODUCTS,
                "query": self.search_data['search_name'],
                "count": self.COUNT_PRODUCTS_PER_PAGE,
            }
            
            domain = store.get("domain")

            url_products = self.URL_PRODUCTS_TEMPLATE.substitute(domain=domain)

            if "near_sucursal" in store:
                url_products = f"{url_products}/region-id/{store['near_sucursal']['sucursal_id']}"
            
            url = build_url(url_products, query_param_products)

            yield scrapy.Request(
                url=url,
                method="GET",
                callback=self.parse,
                meta={"store": store}
            )

    def parse(self, response):

        try:
            store = response.meta["store"]
            from_top_search = response.meta.get("from_top_search", False)
            
            query_search = response.url.split("?")[1]
            query_search = query_search.split("&")[0]
            query_search = query_search.split("=")[1]
            
            response_json = response.json()
            products = response_json["products"]
            product_items = []
            
            item_loader = ItemLoader(item=ProductListItem())
            
            search_data = self.search_data.copy()
            search_data['search_name'] = query_search
            item_loader.add_value("search_data", search_data)
            
            for product in products:
                products_items = product.get("items", [])
                
                for product_item in products_items:

                    price = 0
                    promo_price = 0

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
                        promo_price = comercial_offer["Price"]
                        price = comercial_offer.get("PriceWithoutDiscount")

                    if not comercial_offer.get("AvailableQuantity"):    
                        continue
                    
                    if price == 0 and promo_price == 0:
                        continue
                    
                    if not price:
                        continue
                    
                    product_data = {
                        "search_name" : search_data["search_name"],
                        "product_id": product_item["itemId"],
                        "name": product_item["name"],
                        "description": product_item["complementName"],
                        "url": product["link"],
                        "ean": product_item["ean"],
                        "sku": '',
                        "price": price,
                        "promo_price":promo_price,
                        "images": [image['imageUrl'] for image in product_item["images"] if image['imageUrl']],
                        "store": store,
                        "from_top_search": from_top_search
                    }
                    
                    if store.get("near_sucursal"):
                        product_data["sucursal_price"] = {
                            "sucursal": store["near_sucursal"],
                            "price": price,
                            "promo_price": promo_price
                        }
                    
                    del product_data["store"]["near_sucursal"]
                    
                    if product_data not in product_items:
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

    # Spider instance
    mi_spider_instance = ScrapersVtex

    # run spider
    process = CrawlerProcess()
    process.crawl(
        mi_spider_instance, 
        product_name="manzana"
    )
    process.start()
