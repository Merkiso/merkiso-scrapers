# lib
import datetime
from io import BytesIO
import traceback
import json

# scraper
from scraper_products.db.database import DbConnection
from scraper_products.constants import COLLECTIONS
from scraper_products.settings import MONGO_DB
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
                self.items.append(clean_item)
     
        return item
    
    def close_spider(self, spider):
        products = ProcessData.order_by_product_by_alternate_store(self.items)
        
        for product in products:
            
            print(f"--- product {product.get('name')} ---")
            print(f"--- store {product.get('store').get('name')} ---")
            
            print(f"--- sucursal {product.get('sucursal_price')} ---")
            
            product['created_at'] = datetime.datetime.now().isoformat()
            
            # if already exist, update list of prices_sucursals
            find_product = self.db_connection.find_one(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['products'],
                query={
                    "product_id": product.get("product_id"),
                    "store.name": product.get("store").get("name"),
                }
            )
            
            sucursal_price = product.get("sucursal_price")
            if find_product:
                
                if sucursal_price:
                    
                    sucursal_prices = find_product.get("sucursal_prices", [])
                    
                    # merge list of sucursal prices
                    sucursal_prices.append(sucursal_price)

                    # remove duplicates
                    sucursal_prices = ProcessData.remove_duplicates_sucursal_prices(sucursal_prices)

                    self.db_connection.update_one(
                        db_name=MONGO_DB,
                        collection_name=COLLECTIONS['products'],
                        query={
                            "product_id": product.get("product_id"),
                            "store.name": product.get("store").get("name"),
                        },
                        data={"$set": {"sucursal_prices": sucursal_prices}}
                    )

                else:
                    self.db_connection.update_one(
                        db_name=MONGO_DB,
                        collection_name=COLLECTIONS['products'],
                        query={"product_id": product.get("product_id")},
                        data={"$set": product}
                    )
                
            else:
                product['sucursal_prices'] = []
                if "sucursal_price" in product:
                    product['sucursal_prices'] = [product.get("sucursal_price")]
                    del product['sucursal_price']
                self.db_connection.insert_one(
                    db_name=MONGO_DB,
                    collection_name=COLLECTIONS['products'],
                    data=product
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
            
            sucursal_coordenates = {
                'lat': clean_item.get('lat'),
                'lng': clean_item.get('lng')
            }
            
            # create coordenates_sucursals
            coordenates_sucursals = {
                "sucursal_id": clean_item.get("sucursal_id"),
                "sucursal_name": clean_item.get("name"),
                "user_coordinates": user_coordinates,
                "sucursal_coordenates": sucursal_coordenates,
                "store": clean_item.get("store"),
            }
            
            find_coordenates_sucursals = self.db_connection.find_one(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['client_coordinates_sucursals'],
                query={
                    "sucursal_id": clean_item.get("sucursal_id"),
                    "sucursale_name": clean_item.get("name"),
                    "sucursal_coordenates": sucursal_coordenates,
                    "user_coordinates": user_coordinates,
                }
            )

            if not find_coordenates_sucursals:
                self.db_connection.insert_one(
                    db_name=MONGO_DB,
                    collection_name=COLLECTIONS['client_coordinates_sucursals'],
                    data=coordenates_sucursals
                )

            return item