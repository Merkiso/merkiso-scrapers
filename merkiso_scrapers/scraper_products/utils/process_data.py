from itertools import groupby, zip_longest
import unicodedata
import re

class ProcessData():

    _RE_REMOVE_STYLE_TAG = re.compile(r"(?s)<style>.+</style>")
    _RE_REMOVE_HTML_DATA = re.compile(r'<[^>]+>')
    
    @classmethod
    def clean_fields(cls, data):
        
        for key, value in data.items():
            
            if key != 'images' and key != 'products':
                value = value[0] if isinstance(value, list) else value
                
            if key == 'url':
                store_domain = data.get('store').get('url')
                value = cls.clean_url(store_domain, value)

            if isinstance(value, str):
                field_without_unkwnown_characters = re.sub(r'[^\x20-\x7E]+', '', value)
                field_bytes = field_without_unkwnown_characters.encode('utf-8', errors='ignore')
                field_utf_8 = field_bytes.decode('utf-8', errors='ignore')
                field_without_unicode_scape = re.sub(r'\\u[0-9a-fA-F]{4}', '', field_utf_8)
                
                field_without_style = cls._RE_REMOVE_STYLE_TAG.sub(
                    '', field_without_unicode_scape).strip()
                field_without_html = cls._RE_REMOVE_HTML_DATA.sub(
                    '', field_without_style)

                data[key] = unicodedata.normalize('NFKD', field_without_html.strip())
            data[key] = value
        
        if 'promo_price' in data:
            if data['promo_price'] == data['price']:
                data['promo_price'] = None

        return data
    
    @classmethod
    def remove_duplicates_sucursal_prices(cls, sucursal_prices):
        
        unique_sucursal_prices = []
        
        for sucursal_price in sucursal_prices:
            if sucursal_price not in unique_sucursal_prices:
                unique_sucursal_prices.append(sucursal_price)
        
        return unique_sucursal_prices
    
    @classmethod
    def order_by_product_by_alternate_store(cls, products: list[dict]) -> list[dict]:
        
        ordered_products = []
        
        # Sort the list by store name (this is necessary for groupby to work correctly)
        products.sort(key=lambda x: x['store']['name'])

        group_by_store_dict = {store_name: list(group) for store_name, group in groupby(products, key=lambda x: x['store']['name'])}

        # Iterate over all lists at the same time
        for products_by_store in zip_longest(*group_by_store_dict.values()):
            for product in products_by_store:
                if product:
                    ordered_products.append(product)
                    
        return ordered_products
    
    @classmethod
    def clean_url(cls, store_domain: str, product_url: str):

        path = "/{}".format(product_url) if product_url[0] != '/' else product_url
        url = f"{store_domain}{path}"
        url = re.sub(r'(https?://[^\s]+)(https?://[^\s]+)', r'\2', url)
        
        return url

    @classmethod
    def group_by_store(cls, products: list[dict]) -> list[dict]:
        
        group_by_store_dict = {store_name: list(group) for store_name, group in groupby(products, key=lambda x: x['store']['name'])}
        
        return group_by_store_dict