# lib
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from string import Template
from typing import Final
import traceback
import scrapy

# app
from scraper_products.spiders.scrapers_vtex import ScrapersVtex
from scraper_products.utils.build_url import build_url


class ScrapersVtexTopSearchs(ScrapersVtex):
    name = "scrapers_vtex_top_searchs"
    URL_TOP_SEARCHS_TEMPLATE: Final[str] = Template('https://$domain/api/io/_v/api/intelligent-search/top_searches')
    COUNT_PRODUCTS_PER_PAGE: Final[int] = 100
    
    def __init__(self, **kwargs):
        self.sucursal_ids = kwargs.get("sucursal_ids")

        super(ScrapersVtexTopSearchs, self).__init__(
            "",
            **kwargs
        )

    def start_requests(self):
        
        stores = [store for store in self.get_stores(self.sucursal_ids)]
        
        for store in stores:

            domain = store.get("domain")

            URL_PRODUCTS = self.URL_TOP_SEARCHS_TEMPLATE.substitute(domain=domain)

            yield scrapy.Request(
                url=URL_PRODUCTS,
                method="GET",
                callback=self.parse_top_searchs,
                meta={"store": store}
            )
    
    def parse_top_searchs(self, response):
        try:
            store = response.meta["store"]
            domain = store.get("domain")
            
            response_json = response.json()
            top_searchs = response_json["searches"]
            
            for top_search in top_searchs:
                
                term = top_search["term"]

                query_param_products = {
                    "query": term,
                    "count": self.COUNT_PRODUCTS_PER_PAGE,
                }

                URL_PRODUCTS = self.URL_PRODUCTS_TEMPLATE.substitute(domain=domain)
                
                url = build_url(URL_PRODUCTS, query_param_products)

                yield scrapy.Request(
                    url=url,
                    method="GET",
                    callback=self.parse,
                    meta={"store": store, "from_top_search": True},
                    dont_filter=True
                )
                
        except Exception as e:
            traceback.print_exc()
            raise CloseSpider("Error in parse_top_searchs")

if __name__ == "__main__":

    # Spider instance
    mi_spider_instance = ScrapersVtexTopSearchs

    # run spider
    process = CrawlerProcess()
    process.crawl(
        mi_spider_instance
    )
    process.start()
