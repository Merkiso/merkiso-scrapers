# lib
from scrapy.crawler import CrawlerProcess
from itemloaders import ItemLoader
from string import Template
from typing import Final
import scrapy
import base64
import json

# scraper
from scraper_products.items import ProductInShoppingCarItem, ShoppingCarItem
from scraper_products.structs.items_car_shop import BuildItems
from scraper_products.utils.build_url import build_url


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

    def __init__(
        self, 
        store: str, 
        domain: str, 
        checkout_prefix: str, 
        cart_id: str,
        data: dict, 
        **kwargs
    ):

        # decode base 64 data
        b64_decode_data = base64.b64decode(data)
        b64_decode_data = b64_decode_data.decode("utf-8")
        dict_data = json.loads(b64_decode_data)

        self.store = store
        self.checkout_prefix = checkout_prefix
        self.cart_id = cart_id
        self.build_items: BuildItems = BuildItems.model_validate(dict_data)
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

        url = (
            f"{self.URL_CHECKOUT}{self.PATH_CREATE_CAR_SHOPPING}/{order_form_id}/items"
        )
        url = build_url(url, self.QUERY_PARAM_CREATE_ITEMS_CAR_SHOPPING)

        yield scrapy.Request(
            url=url,
            method="POST",
            body=json.dumps(self.build_items.model_dump()),
            callback=self.parse,
            meta={"order_form_id": order_form_id},
        )

    def parse(self, response):

        order_form_id_param = {"orderFormId": response.meta["order_form_id"]}

        url_checkout = build_url(
            self.URL_CHECKOUT.replace("/api/checkout", self.checkout_prefix),
            order_form_id_param,
        )

        item_loader = ItemLoader(item=ShoppingCarItem())

        products_in_shopping_car = []

        for item in self.build_items.orderItems:
            item_loader_product_in_shopping_car = ItemLoader(
                item=ProductInShoppingCarItem()
            )
            item_loader_product_in_shopping_car.add_value("quantity", item.quantity)
            item_loader_product_in_shopping_car.add_value("product_id", item.id)
            products_in_shopping_car.append(
                item_loader_product_in_shopping_car.load_item()
            )
        
        item_loader.add_value("products", products_in_shopping_car)
        item_loader.add_value("url_purchase", url_checkout)
        item_loader.add_value("cart_id", self.cart_id)
        item_loader.add_value("store", self.store)
        item_loader.add_value("coupon", "")
        
        item_loader_data = item_loader.load_item()
        
        for product in item_loader_data.get("products"):
            for key, value in product.items():
                product[key] = value[0]

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
