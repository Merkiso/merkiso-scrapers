# Description: This file contains the class that process the data from the provider

import re
import unicodedata

class ProcessData():

    _RE_REMOVE_STYLE_TAG = re.compile(r"(?s)<style>.+</style>")
    _RE_REMOVE_HTML_DATA = re.compile(r'<[^>]+>')
    
    @classmethod
    def clean_fields(cls, data):
        
        for key, value in data.items():
            
            if key != 'images' and key != 'products':
                value = value[0]

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
            # missing validate fields to clean double or float or int
        return data
    
    @classmethod
    def remove_duplicates_sucursal_prices(cls, sucursal_prices):
        
        unique_sucursal_prices = []
        
        for sucursal_price in sucursal_prices:
            if sucursal_price not in unique_sucursal_prices:
                unique_sucursal_prices.append(sucursal_price)
        
        return unique_sucursal_prices