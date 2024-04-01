
def wpp_url(data):
    if data['store']['phone']:
        message_initial = f"Hola {data['store']['name']} quiero hacer un pedido en la dirección {"direccion"}%0A"
        product_names = []
        product_names.append(message_initial.replace(" ", "%20"))
        if data['products']:
            for product in data['products']:
                if product['name']:
                    product = f"* {product['name']} con un precio de {product['price']}"
                    product_names.append(product.replace(" ", "%20"))

        final_message = f"%0AMuchas gracias de antemano, Merkiso."
        product_names.append(final_message.replace(" ", "%20"))

        product_names_string = '%0A'.join(product_names)
        
        return f"https://wa.me/{data['store']['phone']}?text={product_names_string}"