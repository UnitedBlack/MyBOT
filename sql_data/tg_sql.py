import sqlite3
import os

db_file = "sql_data\posts.db"


def connect_database(table_name):
    global connection
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            wb_id INTEGER,
            status TEXT
            )"""
    )
    return connection


def is_post_in_db(id_to_check, connection, table_name):
    cursor = connection.cursor()
    cursor.execute(
        f"""
    SELECT wb_id FROM {table_name} WHERE wb_id = ?
    """,
        (id_to_check,),
    )
    row = cursor.fetchone()
    return row if row else False


def get_post_status(id_to_check, connection, table_name):
    cursor = connection.cursor()
    cursor.execute(
        f"""
    SELECT status FROM {table_name} WHERE wb_id = ?
    """,
        (id_to_check,),
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return False


def set_post_status(wb_id, status, connection, table_name):
    cursor = connection.cursor()
    cursor.execute(
        f"""
    UPDATE {table_name} SET status = ? WHERE wb_id = ?
    """,
        (status, wb_id),
    )
    connection.commit()


def add_post(wb_id, connection, table_name, status="Idle"):
    cursor = connection.cursor()
    cursor.execute(
        f"""
    INSERT INTO {table_name} (wb_id, status) VALUES (?, ?)
                   """,
        (wb_id, status),
    )
    connection.commit()


def get_all_posts(connection, table_name):
    cursor = connection.cursor()
    cursor.execute(
        f"""
    SELECT wb_id FROM {table_name}
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


if __name__ == "__main__":
    con = connect_database(db_file=r"sql_data\tp_tgwb.sqlite")
    print(get_all_posts(con))
