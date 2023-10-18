import sqlite3

def create_or_connect_database(db_file):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            discount_price INTEGER,
            price INTEGER,
            star_rating REAL,
            url TEXT,
            pic_url TEXT,
            composition TEXT,
            size TEXT,
            color TEXT
            )
            ''')
    return connection
    
def insert_product(connection, product_data):
    try:
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO products (name, discount_price, price, star_rating, url, pic_url, composition, size, color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product_data["name"], product_data["discount_price"], product_data["price"],
              product_data["star_rating"], product_data["url"], product_data["pic_url"],
              product_data["composition"], product_data["size"], product_data["color"]))

        connection.commit()
        print("Данные успешно добавлены в таблицу.")

    except sqlite3.Error as e:
        print("Ошибка при добавлении данных:", e)
        
    
if __name__ == "__main__":
    product_data = {
            "name": "Примерный продукт",
            "discount_price": 19,
            "price": 29,
            "star_rating": 4,
            "url": "http://example.com/product/123",
            "pic_url": "http://example.com/product/123.jpg",
            "composition": "Состав продукта",
            "size": "M",
            "color": "Синий"
        }
    db_file = "/home/shodan/Documents/Projects/WB/sql_data/WB.sqlite"
    connection = create_or_connect_database(db_file)
    insert_product(connection, product_data)