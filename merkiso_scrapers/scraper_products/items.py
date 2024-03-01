# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ProductListItem(scrapy.Item):
    products = scrapy.Field()
    search_data = scrapy.Field()

class ProductItem(scrapy.Item):
    name = scrapy.Field()
    product_id = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    ean = scrapy.Field()
    sku = scrapy.Field()
    price = scrapy.Field()
    promo_price = scrapy.Field()
    images = scrapy.Field()
    store = scrapy.Field()
    search_name = scrapy.Field()
    
    
class StoreItem(scrapy.Item):
    name = scrapy.Field()
    adress = scrapy.Field()
    url = scrapy.Field()

class ProductInShoppingCarItem(scrapy.Item):
    product_id = scrapy.Field()
    quantity = scrapy.Field()
    
class ShoppingCarItem(scrapy.Item):
    _id = scrapy.Field()
    cart_id = scrapy.Field()
    store = scrapy.Field()
    products = scrapy.Field()
    url_purchase = scrapy.Field()
    coupon = scrapy.Field()
    user_id = scrapy.Field()
