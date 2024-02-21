from io import BytesIO
from .minio_file_manager import minio_files_manager
from .utils.process_data import ProcessData
import traceback
import json

class ScrapersSearhsPipeline:

    search_id: str = None
    
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



