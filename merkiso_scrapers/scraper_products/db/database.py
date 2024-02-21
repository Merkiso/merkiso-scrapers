import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    scoped_session
)

from sqlalchemy.exc import OperationalError
from scraper_products.settings import DATABASE_URL

class DbThreadConnection:

    def __init__(self, pool_size: int = 2, max_overflow: int = 8, pool_recycle = 3600) -> None:
        engine = create_engine(f"sqlite:///{DATABASE_URL}", connect_args={'check_same_thread': False}, poolclass=None)
        self.session = scoped_session(sessionmaker(bind=engine ))
        
        self.engine = engine

    def retry_on_operational_error(func, max_retries=3, retry_interval=1):
        for attempt in range(max_retries):
            try:
                return func()
            except OperationalError as e:
                print(f"OperationalError: {e}. Retrying...")
                time.sleep(retry_interval)
        
        raise Exception("Max retries exceeded. Unable to complete operation.")