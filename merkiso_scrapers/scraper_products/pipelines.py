# lib
from io import BytesIO
import traceback
import json

# scraper
from scraper_products.constants import COLLECTIONS, MONGO_DB
from scraper_products.db.database import DbConnection
from .utils.process_data import ProcessData


class ScrapersSearhsPipeline:

    items: list = []
    
    db_connection = DbConnection()
    
    def process_item(self, item, spider):
        """
        Write items scraped into file.parquet
        """

        if spider.name == "build_car_shopping_vtex":
            return item

        products = item.get('products')

        if products:
            for product in products:
                product_item = dict(product)
                clean_item = ProcessData.clean_fields(product_item)
                
                if clean_item not in self.items:
                    self.items.append(clean_item)

        return item
    
    def close_spider(self, spider):

        if spider.name == "build_car_shopping_vtex":
            return spider

        if self.items:
        
            self.db_connection.insert_many(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['products'],
                data=self.items
            )

     
class CarShoppingPipeline:

    db_connection = DbConnection()
    
    
    def process_item(self, item, spider):
        """
        Write items scraped into file.parquet
        """
        
        if spider.name in {"scrapers_vtex", "scrapers_vtex_top_searchs"}:
            return item
    
        clean_item = ProcessData.clean_fields(item)
        clean_item['user_id'] = None

        self.db_connection.insert_one(
            db_name=MONGO_DB,
            collection_name=COLLECTIONS['checkout_urls'],
            data=clean_item
        )

        return item
