import sqlite3
import os, sys

db_file = "sql_data/tgwb.sqlite"


def create_or_connect_database():
    global connection
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            wb_id INTEGER,
            status TEXT
            )''')
  

def is_post_in_db(id_to_check):
    cursor = connection.cursor()
    cursor.execute('''
    SELECT wb_id FROM posts WHERE wb_id = ?
    ''', (id_to_check,))
    row = cursor.fetchone()
    return row if row else False


def get_post_status(id_to_check):
    cursor = connection.cursor()
    cursor.execute('''
    SELECT status FROM posts WHERE wb_id = ?
    ''', (id_to_check,))
    row = cursor.fetchone()
    print(row)
    if row: return row[0]
    else: return False


def set_post_status(wb_id, status):
    cursor = connection.cursor()
    cursor.execute('''
    UPDATE posts SET status = ? WHERE wb_id = ?
    ''', (status, wb_id))
    connection.commit()
    
    
def add_post(wb_id, status = "Idle"):
    cursor = connection.cursor()
    cursor.execute('''
    INSERT INTO posts (wb_id, status) VALUES (?, ?)
                   ''', (wb_id, status))
    connection.commit()
    
def clear_sql():
    global connection
    if connection:
        connection.close()
        connection = None
    os.remove(db_file)
    
    
if __name__ == "__main__":
    create_or_connect_database()
    set_post_status(wb_id="172838346", status="Liked")
    # print(get_post_status(url_to_check="https://www.wildberries.ru/catalog/66313198/detail.aspx"))
    # print(add_post(url='https://www.wildberries.ru/catalog/6236313198/detail.aspx'))
else:
    create_or_connect_database()
