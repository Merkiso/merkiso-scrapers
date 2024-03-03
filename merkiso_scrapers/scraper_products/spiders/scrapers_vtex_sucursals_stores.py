# lib
from scrapy.crawler import CrawlerProcess
from itemloaders import ItemLoader
from string import Template
from typing import Final
import traceback
import scrapy

# app
from scraper_products.items import ProductListItem, ProductItem, SucursalStoreItem
from scraper_products.utils.build_url import build_url
from scraper_products.db.database import DbConnection


class ScrapersVtexSucursalStores(scrapy.Spider):
    name = "scrapers_vtex_sucursals_stores"
    allowed_domains = []

    URL_NEAR_STORES_TEMPLATE: Final[str] = Template('https://$domain/api/checkout/pub/pickup-points?countryCode=$country_code&geoCoordinates=$lat;$lng')
    URL_STORE_ID_BY_COORDINATES: Final[str] = Template('https://$domain/api/checkout/pub/regions?postalCode=$postal_code&country=$country_code&geoCoordinates=$lat;$lng')

    handle_httpstatus_list = [406, 500]

    def get_stores(self):
        db_connection = DbConnection()
        stores = db_connection.find(
            db_name="merkiso_db",
            collection_name="stores",
            query={}
        )
        return list(stores)
    
    def __init__(self, lat: str, lng: str, **kwargs):
        self.data = {
            "stores": [store for store in self.get_stores()],
            "lat": lat,
            "lng": lng,
        }
        super(ScrapersVtexSucursalStores, self).__init__(**kwargs)


    def start_requests(self):
        for store in self.data['stores']:

            domain = store.get("domain")
            
            url_near_stores = self.URL_NEAR_STORES_TEMPLATE.substitute(
                domain=domain,
                country_code="CO",
                lat=self.data['lat'],
                lng=self.data['lng']
            )
            
            print(f"url_near_stores {url_near_stores}")

            yield scrapy.Request(
                url=url_near_stores,
                method="GET",
                callback=self.get_near_store,
                headers={},
                meta={"store": store}
            )


    def get_near_store(self, response):
        
        print(f"RESPONSE {response.text}")
        
        store = response.meta["store"]
        domain = store.get("domain")
        
        response_json = response.json()
        stores = response_json["items"]

        store_more_near = stores[0]

        store = {
            **store,
            "pickup": store_more_near
        }

        postal_code = store_more_near["pickupPoint"]["address"]["postalCode"]
        lat,lng  = store_more_near["pickupPoint"]["address"]["geoCoordinates"]
        
        url_store_id = self.URL_STORE_ID_BY_COORDINATES.substitute(
            domain=domain,
            country_code="CO",
            lat=lat,
            lng=lng,
            postal_code=postal_code
        )
        
        print(f"url_store_id {url_store_id}")
        
        yield scrapy.Request(
            url=url_store_id,
            method="GET",
            callback=self.parse,
            meta={"store": store}
        )


    def parse(self, response):
        
        print(f"response ids sucursals {response.json()}")
        
        try:
            store = response.meta["store"]
            response_json = response.json()
            sucural_id = response_json[0]["id"]

            full_address = f"{store['pickup']['pickupPoint']['address']['state']}-{store['pickup']['pickupPoint']['address']['city']}, {store['pickup']['pickupPoint']['address']['neighborhood']}-{store['pickup']['pickupPoint']['address']['street']}"

            if not store['pickup']['pickupPoint']['address']['neighborhood']:
                full_address = f"{store['pickup']['pickupPoint']['address']['state']}-{store['pickup']['pickupPoint']['address']['city']}, {store['pickup']['pickupPoint']['address']['street']}"            

            store_pickup = {
                "sucursal_id": sucural_id,
                "name": f"{store['name']}-{full_address}",
                "lat": store['pickup']['pickupPoint']['address']['geoCoordinates'][0],
                "lng": store['pickup']['pickupPoint']['address']['geoCoordinates'][1],
            }
            
            del store['pickup']
            
            store_pickup['store'] = store
            
            item_loader = ItemLoader(item=SucursalStoreItem())
            
            for key, value in store_pickup.items():
                item_loader.add_value(key, value)
            
            item_loader_data = item_loader.load_item()
            item_loader_data['user_coordinates'] = {
                "lat": float(self.data['lat']),
                "lng": float(self.data['lng'])
            }
            
            yield item_loader_data
            
        except Exception as e:
            traceback.print_exc()
            yield {"error": True}

    def create_item_product(self, product_data):

        item_loader = ItemLoader(item=ProductItem())
        
        for key, value in product_data.items():
            item_loader.add_value(key, value)

        return item_loader.load_item()

    

if __name__ == "__main__":

    # Spider instance
    mi_spider_instance = ScrapersVtexSucursalStores

    # run spider
    process = CrawlerProcess()
    process.crawl(
        mi_spider_instance, 
        product_name="manzana"
    )
    process.start()
