from scrapers_searchs.db.database import DbThreadConnection
from scrapers_searchs.db.models.stores import Store

db_scoped_connection = DbThreadConnection(pool_size = 10, max_overflow = 15, pool_recycle = -1)

def create_stores():

    # Create a sample DataFrame
    data_list = [
        {'name': 'Euro', 'url': 'https://www.eurosupermercados.com.co', 'domain': 'www.eurosupermercados.com.co'},
        {'name': 'Olimpica', 'url': 'https://www.olimpica.com', 'domain': 'www.olimpica.com'},
        {'name': 'Exito', 'url': 'https://www.exito.com', 'domain': 'www.exito.com'},
        {'name': 'Jumbo', 'url': 'https://www.tiendasjumbo.co', 'domain': 'www.tiendasjumbo.co'},
        {'name': 'Carulla', 'url': 'https://www.carulla.com', 'domain': 'www.carulla.com'},
        {'name': 'Metro', 'url': 'https://www.tiendasmetro.co', 'domain': 'www.tiendasmetro.co'},
    ]

    with db_scoped_connection.session() as db_session:
        
        all_stores = db_session.query(Store).all()
        
        if all_stores:
            return
        
        for data in data_list:
            store = Store(
                name = data["name"],
                url = data["url"],
                domain = data["domain"],
            )
            db_session.add(store)
        db_session.commit()
