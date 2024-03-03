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

        if spider.name in {"build_car_shopping_vtex", "scrapers_vtex_sucursals_stores"}:
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

        if spider.name in {"build_car_shopping_vtex", "scrapers_vtex_sucursals_stores"}:
            return spider

        if self.items:
            
            for item in self.items:
                
                # if already exist, update list of prices_sucursals
                find_product = self.db_connection.find_one(
                    db_name=MONGO_DB,
                    collection_name=COLLECTIONS['products'],
                    query={"product_id": item.get("product_id")}
                )
                
                if find_product:
                    # merge list of sucursal prices
                    sucursal_prices = find_product.get("sucursal_prices")
                    sucursal_prices.extend(item.get("sucursal_prices"))
                    
                    # remove duplicates
                    sucursal_prices = list({v['sucursal_id']:v for v in sucursal_prices}.values())
                    
                    self.db_connection.update_one(
                        db_name=MONGO_DB,
                        collection_name=COLLECTIONS['products'],
                        query={"product_id": item.get("product_id")},
                        data={"$set": {"sucursal_prices": sucursal_prices}}
                    )

     
class CarShoppingPipeline:

    db_connection = DbConnection()
    
    
    def process_item(self, item, spider):
        """
        Write items scraped into db
        """
        
        if spider.name in {"scrapers_vtex_sucursals_stores","scrapers_vtex", "scrapers_vtex_top_searchs"}:
            return item
    
        clean_item = ProcessData.clean_fields(item)
        clean_item['user_id'] = None

        # check if already urls in cart, update
        find_checkout_urls_of_cart = self.db_connection.find(
            db_name=MONGO_DB,
            collection_name=COLLECTIONS['checkout_urls'],
            query={
                "cart_id": clean_item.get("cart_id"),
                "store.name": clean_item.get("store").get("name"),
            }
        )
        
        if find_checkout_urls_of_cart:
            self.db_connection.delete_one(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['checkout_urls'],
                query={"cart_id": clean_item.get("cart_id")},
            )

        self.db_connection.insert_one(
            db_name=MONGO_DB,
            collection_name=COLLECTIONS['checkout_urls'],
            data=clean_item
        )

        return item

class VtextSucursalStoresPipeline:
    
        db_connection = DbConnection()
    
        def process_item(self, item, spider):
            """
            Write items scraped into db
            """


            if spider.name in {"build_car_shopping_vtex","scrapers_vtex", "scrapers_vtex_top_searchs"}:
                return item

            user_coordinates = item.get("user_coordinates")
            del item['user_coordinates']
            
            clean_item = ProcessData.clean_fields(item)

            sucursal = self.db_connection.find_one(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['sucursals'],
                query={"sucursal_id": clean_item.get("sucursal_id")}
            )
            
            if sucursal:
                self.db_connection.update_one(
                    db_name=MONGO_DB,
                    collection_name=COLLECTIONS['sucursals'],
                    query={
                        "sucursal_id": clean_item.get("sucursal_id"),
                        "name": clean_item.get("name"),
                    },
                    data={"$set": clean_item}
                )
            else:
                self.db_connection.insert_one(
                    db_name=MONGO_DB,
                    collection_name=COLLECTIONS['sucursals'],
                    data=clean_item
                )
            
            # create coordenates_sucursals
            coordenates_sucursals = {
                "sucursal_id": clean_item.get("sucursal_id"),
                "sucursale_name": clean_item.get("name"),
                "coordenates": user_coordinates,
                "store": clean_item.get("store"),
            }
            
            find_coordenates_sucursals = self.db_connection.find_one(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['client_coordinates_sucursals'],
                query={
                    "sucursal_id": clean_item.get("sucursal_id"),
                    "sucursale_name": clean_item.get("name"),
                    "coordenates": user_coordinates,
                }
            )

            if not find_coordenates_sucursals:
                self.db_connection.insert_one(
                    db_name=MONGO_DB,
                    collection_name=COLLECTIONS['client_coordinates_sucursals'],
                    data=coordenates_sucursals
                )

            return item