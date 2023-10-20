import sqlite3

db_file = "/home/shodan/Documents/Projects/WB/sql_data/WB.sqlite"

def create_or_connect_database():
    global connection
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
    
def insert_product(product_data):
    try:
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO products (name, discount_price, price, star_rating, url, pic_url, composition, size, color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product_data["name"], product_data["price"], product_data["discount_price"],
              product_data["star_rating"], product_data["url"], product_data["pic_url"],
              product_data["composition"], product_data["size"], product_data["color"]))
        connection.commit()
        print("Данные успешно добавлены в таблицу.")

    except sqlite3.Error as e:
        print("Ошибка при добавлении данных:", e)
        

def is_product_in_database(url_to_check):
    cursor = connection.cursor()
    cursor.execute('''
    SELECT url FROM products WHERE url = ?
    ''', (url_to_check,))
    row = cursor.fetchone()
    return row is not None
        
def get_all_products():
    cursor = connection.cursor()
    cursor.execute('''
    SELECT * FROM products
    ''')
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in rows]
    return result
        
if __name__ == "__main__":
    # product_data = {
    #     "name": "Примерный продукт", "discount_price": 19, "price": 29,
    #     "star_rating": 4, "url": "http://example.com/product/123",
    #     "pic_url": "http://example.com/product/123.jpg",
    #     "composition": "Состав продукта", "size": "M",
    #     "color": "Синий"
    #     }
    create_or_connect_database()
    # insert_product(connection, product_data)
    # print(check_product())
    # urls = ["https://www.wildberries.ru/catalog/13353225612/detail.aspx", "https://www.wildberries.ru/catalog/155776950/detail.aspx", "https://www.wildberries.ru/catalog/172889887/detail.aspx"]
    # for url in urls:
    #     print(is_product_in_database(url))
    get_all_products()
else:
    create_or_connect_database()