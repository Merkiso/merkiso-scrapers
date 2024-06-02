# lib
import datetime
import time

# scraper
from scraper_products.db.database import DbConnection
from scraper_products.constants import COLLECTIONS
from scraper_products.settings import MONGO_DB
from .utils.process_data import ProcessData
from .utils.wapp_url import wpp_url
import threading
import re


class ScrapersSearhsPipeline:

    items: list[dict] = []
    
    db_connection = DbConnection()


    def process_item(self, item, spider):
        """
        Write items scraped into file.parquet
        """
        print(f" item {item} spider {spider.name} ")

        if spider.name in {"build_car_shopping_vtex", "scrapers_vtex_sucursals_stores", "scrapers_vtex_top_searchs"}:
            return item

        products = item.get('products')

        if products:
            for product in products:
                product_item = dict(product)
                clean_item = ProcessData.clean_fields(product_item)
                self.items.append(clean_item)

        return item

    def close_spider(self, spider):
        """
        Write items scraped into db
        """

        products_group_by_store = ProcessData.group_by_store(self.items)
        
        for store_name, products in products_group_by_store.items():
            
            search_term = products[0].get("search_term")
            store = products[0].get("store")
            store_name = products[0].get("store").get("name")
            sucursal = store.get("near_sucursal")
            from_top_search = products[0].get("from_top_search")

            self.db_connection.delete_one(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['products_raw'],
                query={
                    "search_term": search_term,
                    "store_name": store_name,
                    "sucursal": sucursal,
                    "from_top_search": from_top_search,
                }
            )
            
            self.db_connection.insert_one(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['products_raw'],
                data={
                    "search_term": search_term,
                    "store_name": store_name,
                    "sucursal": sucursal,
                    "from_top_search": from_top_search,
                    "products": products,
                }
            )

class ScrapersTopSearhsPipeline:
    
    db_connection = DbConnection()

    def process_item(self, item, spider):
        """
        Write items scraped into file.parquet
        """
        print(f"item {item} spider {spider.name} ")

        if spider.name in {"build_car_shopping_vtex", "scrapers_vtex_sucursals_stores", "scrapers_vtex"}:
            return item

        products = item.get('products')
        items = []
        
        if products:
            for product in products:
                product_item = dict(product)
                clean_item = ProcessData.clean_fields(product_item)
                items.append(clean_item)

            search_term = products[0].get("search_term")
            store = products[0].get("store")
            store_name = products[0].get("store").get("name")
            sucursal = store.get("near_sucursal")
            from_top_search = products[0].get("from_top_search")

            self.db_connection.delete_one(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['products_raw'],
                query={
                    "search_term": search_term,
                    "store_name": store_name,
                    "sucursal": sucursal,
                    "from_top_search": from_top_search,
                }
            )
            
            self.db_connection.insert_one(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['products_raw'],
                data={
                    "search_term": search_term,
                    "store_name": store_name,
                    "sucursal": sucursal,
                    "from_top_search": from_top_search,
                    "products": products,
                }
            )
        return item

    def close_spider(self, spider):
        pass


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
        # get products
        wp_url = wpp_url(clean_item)
        clean_item['url_purchase_wp'] = wp_url
        if find_checkout_urls_of_cart:
            self.db_connection.update_one(
                db_name=MONGO_DB,
                collection_name=COLLECTIONS['checkout_urls'],
                query={
                    "cart_id": clean_item.get("cart_id"),
                    "store.name": clean_item.get("store").get("name"),
                },
                data={"$set": clean_item}
            )
        else:
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

            return item