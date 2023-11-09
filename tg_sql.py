import sqlite3
import os


def connect_database(db_file):
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
    return connection


def is_post_in_db(id_to_check, connection):
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT wb_id FROM posts WHERE wb_id = ?
    """,
        (id_to_check,),
    )
    row = cursor.fetchone()
    return row if row else False


def get_post_status(id_to_check, connection):
    cursor = connection.cursor()
    cursor.execute(
        """
    SELECT status FROM posts WHERE wb_id = ?
    """,
        (id_to_check,),
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return False


def set_post_status(wb_id, status, connection):
    cursor = connection.cursor()
    cursor.execute(
        """
    UPDATE posts SET status = ? WHERE wb_id = ?
    """,
        (status, wb_id),
    )
    connection.commit()


def add_post(wb_id, connection, status="Idle"):
    cursor = connection.cursor()
    cursor.execute(
        """
    INSERT INTO posts (wb_id, status) VALUES (?, ?)
                   """,
        (wb_id, status),
    )
    connection.commit()


def get_all_posts(connection):
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


def clear_db(db_file):
    try:
        os.remove(db_file)
    except FileNotFoundError:
        return


def close_connection(connection):
    connection.close()
