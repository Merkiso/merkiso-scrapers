# lib
from io import BytesIO
import traceback
import json

# scraper
from scraper_products.constants import FILENAME_PRODUCTS
from .minio_file_manager import minio_files_manager
from .utils.process_data import ProcessData


class ScrapersSearhsPipeline:

    items: list = []
    
    def process_item(self, item, spider):
        """
        Write items scraped into file.parquet
        """

        products = item.get('products')

        if products:
            for product in products:
                product_item = dict(product)
                clean_item = ProcessData.clean_fields(product_item)
                self.items.append(clean_item)

        return item
    
    def close_spider(self, spider):

        if spider.name in {"scrapers_vtex_top_searchs"}:
            return

        products_json = json.dumps({
            "search": {
                "name": spider.search_data['search_name'],
                "status": "completed"
            },
            "products": self.items
        })
        products_bytes_data = products_json.encode('utf-8')
        try:
            minio_files_manager.upload_public_file(
                filename=spider.search_data['search_name'],
                data=BytesIO(products_bytes_data),
            )
        except Exception as e:
            traceback.print_exc()



class ScrapersTopSearhsPipeline(ScrapersSearhsPipeline):
    
    def close_spider(self, spider):

        if spider.name in {"scrapers_vtex"}:
            return

        products_json = json.dumps({
            "search": {
                "name": 'top_searchs',
                "status": "completed"
            },
            "products": self.items
        })
        products_bytes_data = products_json.encode('utf-8')
        try:
            minio_files_manager.upload_public_file(
                filename=FILENAME_PRODUCTS,
                data=BytesIO(products_bytes_data),
            )
        except Exception as e:
            traceback.print_exc()