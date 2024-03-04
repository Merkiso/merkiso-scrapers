# lib
from scrapy.crawler import CrawlerProcess
from itemloaders import ItemLoader
from string import Template
from typing import Final
import scrapy
import base64
import json

# scraper
from scraper_products.constants import COLLECTIONS, FIELD_NAME_CAR_ITEMS
from scraper_products.utils.build_url import build_url
from scraper_products.db.database import DbConnection
from scraper_products.items import ShoppingCarItem
from scraper_products.settings import MONGO_DB


class BuildCarShopingVtex(scrapy.Spider):
    name = "build_car_shopping_vtex"
    allowed_domains = []

    URL_CHECKOUT: Final[str] = Template("https://$domain/api/checkout")
    PATH_CREATE_CAR_SHOPPING: Final[str] = "/pub/orderForm"
    QUERY_PARAM_CREATE_CAR_SHOPPING: Final[dict] = {
        "forceNewCart": "true",
    }
    QUERY_PARAM_CREATE_ITEMS_CAR_SHOPPING: Final[dict] = {
        "allowedOutdatedData": "paymentData",
    }
    
    stores: list = []
    store: dict = {}

    db_connection = DbConnection()
    
    def __init__(
        self, 
        cart_id: str,
        store: str = None, 
        **kwargs
    ):

        if store:
            # decode base 64 data
            b64_decode_data = base64.b64decode(store)
            b64_decode_data = b64_decode_data.decode("utf-8")
            dict_data = json.loads(b64_decode_data)
            self.store = dict_data
            
        self.cart_id = cart_id
        
        self.load_init_data()
        
        super(BuildCarShopingVtex, self).__init__(**kwargs)

    def load_init_data(self):
        self.cart = self.db_connection.find_one(
            collection_name=COLLECTIONS["shopping_carts"],
            db_name=MONGO_DB,
            query={"cart_id": self.cart_id},
        )
        
        self.stores.append(self.store)
        
        if not self.store:
            
            stores_in_products = set(
                [product.get("store").get("name") for product in self.cart.get("products")]
            )
            
            self.stores = self.db_connection.find(
                collection_name=COLLECTIONS["stores"],
                db_name=MONGO_DB,
                query={"name": {"$in": list(stores_in_products)}},
            )
            self.stores = list(self.stores)
        
    
    def start_requests(self):
        
        for store in self.stores:
            
            store_domain = store.get("domain")

            url = self.URL_CHECKOUT.substitute(domain=store_domain)
            url = f"{url}{self.PATH_CREATE_CAR_SHOPPING}"
            url = build_url(url, self.QUERY_PARAM_CREATE_CAR_SHOPPING)

            yield scrapy.Request(
                url=url,
                method="GET",
                callback=self.post_save_items,
                meta={
                    "store": store,
                    "url": url,
                }
            )

    def post_save_items(self, response):
        store = response.meta["store"]
        store_domain = store.get("domain")
        
        response_json = response.json()
        order_form_id = response_json["orderFormId"]

        url = self.URL_CHECKOUT.substitute(domain=store_domain)
        url = (
            f"{url}{self.PATH_CREATE_CAR_SHOPPING}/{order_form_id}/items"
        )
        url = build_url(url, self.QUERY_PARAM_CREATE_ITEMS_CAR_SHOPPING)
        
        products_from_cart = self.cart.get("products")
        
        build_items = {
            FIELD_NAME_CAR_ITEMS: [
                {
                    "quantity": product.get("quantity_cart"),
                    "seller": "1",
                    "id": product.get("product_id"),
                    "index": 0,
                }
                for product in products_from_cart
                if product.get("store").get("name") == store.get("name")
                ]
        }

        yield scrapy.Request(
            url=url,
            method="POST",
            body=json.dumps(build_items),
            callback=self.parse,
            meta={
                "order_form_id": order_form_id,
                "store": store,
            },
        )

    def parse(self, response):
        

        store = response.meta["store"]
        checkout_prefix = store.get("checkout_prefix")

        order_form_id_param = {"orderFormId": response.meta["order_form_id"]}

        url_checkout:str = self.URL_CHECKOUT.substitute(domain=store.get("domain"))

        url_checkout = build_url(
            url_checkout.replace('/api/checkout', checkout_prefix),
            order_form_id_param,
        )

        item_loader = ItemLoader(item=ShoppingCarItem())

        products_in_shopping_car = []
        
        for product in self.cart.get("products"):
            
            if product.get("store").get("name") == store.get("name"):
                products_in_shopping_car.append(product)
    
        item_loader.add_value("products", products_in_shopping_car)
        item_loader.add_value("url_purchase", url_checkout)
        item_loader.add_value("cart_id", self.cart_id)
        item_loader.add_value("store", store)
        item_loader.add_value("coupon", "")
        
        item_loader_data = item_loader.load_item()
        
        yield item_loader_data


if __name__ == "__main__":

    # Instancia el spider
    mi_spider_instance = BuildCarShopingVtex

    # Configura y ejecuta el proceso de Scrapy
    process = CrawlerProcess()
    process.crawl(
        mi_spider_instance,
        data={
            "orderItems": [
                {"quantity": 3, "seller": "1", "id": "176910", "index": 0},
                {"quantity": 1, "seller": "1", "id": "776582", "index": 0},
            ]
        },
        domain="www.olimpica.com",
    )
    process.start()
