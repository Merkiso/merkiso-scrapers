# lib
import json
import time
import uuid
from bson.objectid import ObjectId
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from itemloaders import ItemLoader
from string import Template
from typing import Final
import traceback
import scrapy
import base64

# app
from scraper_products.items import ProductItem, ProductListItem
from scraper_products.utils.build_url import build_url
from scraper_products.db.database import DbConnection
from scraper_products.constants import COLLECTIONS
from scraper_products.settings import MONGO_DB

class ScrapersVtexTopSearchs(scrapy.Spider):
    name = "scrapers_vtex_top_searchs"
    URL_TOP_SEARCHS_TEMPLATE: Final[str] = Template('https://$domain/api/io/_v/api/intelligent-search/top_searches')
    URL_PRODUCTS_TEMPLATE: Final[str] = Template('https://$domain/api/io/_v/api/intelligent-search/product_search')
    COUNT_PRODUCTS_PER_PAGE: Final[int] = 100

    db_connection = DbConnection()
    
    handle_httpstatus_list = [406]
    
    def __init__(self, **kwargs):
        self.sucursal_ids = kwargs.get('sucursal_ids', '') or ''
        self.store = kwargs.get('store', '') or ''

        
    def create_item_product(self, product_data):

        item_loader = ItemLoader(item=ProductItem())
        
        for key, value in product_data.items():
            item_loader.add_value(key, value)

        return item_loader.load_item()

    def get_near_sucursal(
        self,
        store: dict,
        ids: str,
    ):  

        #decode ids from base64 asda
        decode_ids_b64 = base64.b64decode(ids)
        decode_ids_b64 = decode_ids_b64.decode('utf-8')
        decode_ids_b64 = json.loads(decode_ids_b64)
        ids = [ObjectId(_id) for _id in decode_ids_b64]
        
        stores_sucursals = list(self.db_connection.find(
            db_name=MONGO_DB,
            collection_name=COLLECTIONS['sucursals'],
            query={
                "_id": {"$in": ids}
            }
        ))

        if stores_sucursals:
            store_sucursal = list(
                filter(
                    lambda x: str(x["store"]["_id"]) == store["_id"],
                    stores_sucursals
                )
            )
            
            if store_sucursal:
                return store_sucursal[0]

    def start_requests(self):
        
        decode_store_b64 = base64.b64decode(self.store)
        decode_store_b64 = decode_store_b64.decode('utf-8')
        store = json.loads(decode_store_b64)

        if self.sucursal_ids:
            near_sucursal = self.get_near_sucursal(store, self.sucursal_ids)
            if near_sucursal:
                store["near_sucursal"] = near_sucursal

        domain = store.get("domain")

        URL_PRODUCTS = self.URL_TOP_SEARCHS_TEMPLATE.substitute(domain=domain)

        yield scrapy.Request(
            url=URL_PRODUCTS,
            method="GET",
            callback=self.parse_top_searchs,
            meta={"store": store}
        )
    
    def parse_top_searchs(self, response):
        try:
            store = response.meta["store"]
            domain = store.get("domain")
            
            response_json = response.json()
            top_searchs = response_json["searches"]
            
            for top_search in top_searchs:
                
                term = top_search["term"]

                query_param_products = {
                    "query": term,
                    "count": self.COUNT_PRODUCTS_PER_PAGE,
                }

                url_products = self.URL_PRODUCTS_TEMPLATE.substitute(domain=domain)

                if "near_sucursal" in store:
                    url_products = f"{url_products}/region-id/{store['near_sucursal']['sucursal_id']}"
                
                url = build_url(url_products, query_param_products)

                yield scrapy.Request(
                    url=url,
                    method="GET",
                    callback=self.parse,
                    meta={"store": store},
                    dont_filter=True
                )
                
        except Exception as e:
            traceback.print_exc()
            raise CloseSpider("Error in parse_top_searchs")

    def parse(self, response):

        try:
            store = response.meta["store"]
            
            query_search = response.url.split("?")[1]
            query_search = query_search.split("&")[0]
            query_search = query_search.split("=")[1]
            
            response_json = response.json()
            products = response_json["products"]
            product_items = []
            
            item_loader = ItemLoader(item=ProductListItem())
            
            search_data = {
                "search_term": '',
                "store": {
                    "id": str(store["_id"]),
                    "name": store["name"],
                    "url": store["url"],
                    "phone": store["phone"],
                    "domain": store["domain"],
                    "near_sucursal": store.get('near_sucursal'),
                }
            }
            search_data['search_term'] = query_search.replace("+", " ")
            item_loader.add_value("search_data", search_data)
            
            for product in products:
                products_items = product.get("items", [])
                
                # get categorization
                categorization = product.get("categories", [])
                
                department = ""
                category = ""
                subcategory = ""
                
                if categorization:
                    categorization = categorization[0].split("/")
                    
                    index_cat = 0
                    
                    for cat in categorization:
                        if cat != '':
                            if index_cat == 0:
                                department = cat
                            elif index_cat == 1:
                                category = cat
                            elif index_cat == 2:
                                subcategory = cat
                            index_cat += 1
 
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
                        "id": str(uuid.uuid4()),
                        "search_term" : search_data["search_term"],
                        "product_id": product_item["itemId"],
                        "name": product_item["name"],
                        "description": product_item["complementName"],
                        "url": product["link"],
                        "ean": product_item["ean"],
                        "sku": '',
                        "price": price,
                        "promo_price":promo_price,
                        "images": [image['imageUrl'] for image in product_item["images"] if image['imageUrl']],
                        "department": department,
                        "category": category,
                        "subcategory": subcategory,
                        "store": search_data["store"],
                        "from_top_search": True
                    }
                    
                    if product_data not in product_items:
                        product_items.append(self.create_item_product(product_data))
            
            item_loader.add_value("products", product_items)
            yield item_loader.load_item()
        except Exception as e:
            traceback.print_exc()
            yield {"error": True}



if __name__ == "__main__":

    # Spider instance
    mi_spider_instance = ScrapersVtexTopSearchs

    # run spider
    process = CrawlerProcess()
    process.crawl(
        mi_spider_instance
    )
    process.start()
