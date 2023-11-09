import sqlite3
import os


def connect_database(db_file):
    # global connection
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            wb_id INTEGER,
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
            """
    )
    return connection


def insert_product(product_data, connection):
    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO products (wb_id, name, discount_price, price, star_rating, url, pic_url, composition, size, color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                product_data["wb_id"],
                product_data["name"],
                product_data["price"],
                product_data["discount_price"],
                product_data["star_rating"],
                product_data["url"],
                product_data["pic_url"],
                product_data["composition"],
                product_data["size"],
                product_data["color"],
            ),
        )
        connection.commit()
        print("Данные успешно добавлены в таблицу.")

    except sqlite3.Error as e:
        print("Ошибка при добавлении данных:", e)


def is_product_in_database(url_to_check, connection):
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT url FROM products WHERE url = ?
    """,
        (url_to_check,),
    )
    row = cursor.fetchone()
    return row is not None


def get_all_products(connection):
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT * FROM products
    """
    )
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in rows]
    return result


def clear_db(db_file):
    try:
        os.remove(db_file)
    except FileNotFoundError:
        return
    except PermissionError:
        print("Закройте все процессы с БД!")
        exit()


def close_connection(connection):
    connection.close()


# if __name__ == "__main__":
#     create_or_connect_database()
# else:
#     create_or_connect_database()
