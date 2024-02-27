from scraper_products.db.database import DbConnection

db_connection = DbConnection()

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
    stores_collection = db_connection.get_collection(db_name="merkiso_db", collection_name="stores")

    # Crea un índice único en el campo 'name'
    stores_collection.create_index([('name', 1)], unique=True)

    for doc in data_list:
        
        store = db_connection.find_one(
            db_name="merkiso_db", 
            collection_name="stores", 
            query={
                "url": doc["url"]
            }
        )
        
        if store:
            db_connection.update_one(
                db_name="merkiso_db",
                collection_name="stores",
                query={"url": doc["url"]},
                data={"$set": doc}
            )
            continue
        
        db_connection.insert_one(
            db_name="merkiso_db",
            collection_name="stores",
            data=doc
        )

if __name__ == "__main__":
    create_stores()