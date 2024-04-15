# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst


class ProductListItem(scrapy.Item):
    products = scrapy.Field()
    search_data = scrapy.Field(output_processor=TakeFirst())
    store = scrapy.Field(output_processor=TakeFirst())

class ProductItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    product_id = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    ean = scrapy.Field(output_processor=TakeFirst())
    sku = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    promo_price = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field()
    store = scrapy.Field(output_processor=TakeFirst())
    search_term = scrapy.Field(output_processor=TakeFirst())
    sucursal_price = scrapy.Field(output_processor=TakeFirst())
    from_top_search = scrapy.Field(output_processor=TakeFirst())
    
    
class StoreItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    adress = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())

class ProductInShoppingCarItem(scrapy.Item):
    product_id = scrapy.Field(output_processor=TakeFirst())
    quantity = scrapy.Field(output_processor=TakeFirst())
    
class ShoppingCarItem(scrapy.Item):
    _id = scrapy.Field(output_processor=TakeFirst())
    cart_id = scrapy.Field(output_processor=TakeFirst())
    store = scrapy.Field(output_processor=TakeFirst())
    products = scrapy.Field()
    url_purchase = scrapy.Field(output_processor=TakeFirst())
    coupon = scrapy.Field(output_processor=TakeFirst())
    user_id = scrapy.Field(output_processor=TakeFirst())
    url_purchase_wp = scrapy.Field(output_processor=TakeFirst())

class SucursalStoreItem(scrapy.Item):
    _id = scrapy.Field(output_processor=TakeFirst())
    store = scrapy.Field(output_processor=TakeFirst())
    sucursal_id = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    lng = scrapy.Field(output_processor=TakeFirst())
    lat = scrapy.Field(output_processor=TakeFirst())
    user_coordinates = scrapy.Field(output_processor=TakeFirst())