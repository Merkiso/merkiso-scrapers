PATH_PARQUETS = '/app-db-data/parquet/'
FULL_PATH_PARQUET_STORES = f'{PATH_PARQUETS}stores.parquet'
FULL_PATH_PARQUET_PRODUCTS = f'{PATH_PARQUETS}products.parquet'
FULL_PATH_PARQUET_SEARCHS = f'{PATH_PARQUETS}searchs.parquet'
FILENAME_PRODUCTS = 'products'
FIELD_NAME_CAR_ITEMS = "orderItems"

MONGO_DB = "merkiso_db"
COLLECTIONS = {
    "stores": "stores",
    "products": "products",
    "searchs": "searchs",
    "shopping_carts": "shopping_carts",
    "checkout_urls": "checkout_urls",
}

STATUS_SEARCH = {
    "running": "running",
    "completed": "completed",
    "failed": "failed",
}
