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

        products = item.get('products')

        if products:
            for product in products:
                product_item = dict(product)
                clean_item = ProcessData.clean_fields(product_item)
                
                if clean_item not in self.items:
                    self.items.append(clean_item)

        return item
    
    def close_spider(self, spider):
        
        if self.items:
        
            self.db_connection.insert_many(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['products'],
                data=self.items
            )