import sqlite3
import os, sys

db_file = "sql_data/tgwb.sqlite"


def create_or_connect_database():
    global connection
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            wb_id INTEGER,
            status TEXT
            )"""
    )


def is_post_in_db(id_to_check):
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT wb_id FROM posts WHERE wb_id = ?
    """,
        (id_to_check,),
    )
    row = cursor.fetchone()
    return row if row else False


def get_post_status(id_to_check):
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT status FROM posts WHERE wb_id = ?
    """,
        (id_to_check,),
    )
    row = cursor.fetchone()
    # print(id_to_check)
    # print(row)
    if row:
        return row[0]
    else:
        return False


def set_post_status(wb_id, status):
    cursor = connection.cursor()
    cursor.execute(
        """
    UPDATE posts SET status = ? WHERE wb_id = ?
    """,
        (status, wb_id),
    )
    connection.commit()


def add_post(wb_id, status="Idle"):
    cursor = connection.cursor()
    cursor.execute(
        """
    INSERT INTO posts (wb_id, status) VALUES (?, ?)
                   """,
        (wb_id, status),
    )
    connection.commit()


def get_all_posts():
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT wb_id FROM posts
    """
    )
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    result = [dict(zip(column_names, row)) for row in rows]
    res = [row[0] for row in rows]
    return res


def clear_db():
    # global connection
    # connection.close()
    # connection = None
    try:
        os.remove(db_file)
    except FileNotFoundError:
        return
    
def close_connection():
    global connection
    connection.close()


if __name__ == "__main__":
    create_or_connect_database()
    # set_post_status(wb_id="172838346", status="Liked")
    # print(get_all_posts())
    get_all_posts()
else:
    # clear_db()
    create_or_connect_database()
