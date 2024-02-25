# lib
from sqlalchemy import Column, Integer, String

# scraper
from scraper_products.db.base import Base

class Store(Base):
    __tablename__ = 'stores'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    domain = Column(String)
    logo = Column(String)

    def __json__(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "domain": self.domain,
            "logo": self.logo,
        }