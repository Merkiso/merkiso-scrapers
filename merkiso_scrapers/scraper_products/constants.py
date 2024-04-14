PATH_PARQUETS = '/app-db-data/parquet/'
FULL_PATH_PARQUET_STORES = f'{PATH_PARQUETS}stores.parquet'
FULL_PATH_PARQUET_PRODUCTS = f'{PATH_PARQUETS}products.parquet'
FULL_PATH_PARQUET_SEARCHS = f'{PATH_PARQUETS}searchs.parquet'
FILENAME_PRODUCTS = 'products'
FIELD_NAME_CAR_ITEMS = "orderItems"

COLLECTIONS = {
    "stores": "stores",
    "products": "products",
    "searchs": "searchs",
    "shopping_carts": "shopping_carts",
    "checkout_urls": "checkout_urls",
    "sucursals": "sucursals",
    "client_coordinates_sucursals": "client_coordinates_sucursals",
    "products_raw": "products_raw",
}

STATUS_SEARCH = {
    "running": "running",
    "completed": "completed",
    "failed": "failed",
}
