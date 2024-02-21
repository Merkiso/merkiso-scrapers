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
    availability = scrapy.Field()
    price = scrapy.Field()
    images = scrapy.Field()
    store = scrapy.Field()
    search_name = scrapy.Field()
    
    
class StoreItem(scrapy.Item):
    name = scrapy.Field()
    adress = scrapy.Field()
    url = scrapy.Field()

class ProductInShoppingCarItem(scrapy.Item):
    product = scrapy.Field()
    quantity = scrapy.Field()
    amount = scrapy.Field()
    
class ShoppingCarItem(scrapy.Item):
    store = scrapy.Field()
    products = scrapy.Field()
    amount = scrapy.Field()
    url_purchase = scrapy.Field()
    coupon = scrapy.Field()