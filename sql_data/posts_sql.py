import sqlite3
import os

db_file = "sql_data\sources\posts.db"


def connect_database(table_name):
    # global connection
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


def is_post_in_db(id_to_check, table_name):
    cursor = connect_database(table_name).cursor()
    cursor.execute(
        f"""
    SELECT wb_id FROM {table_name} WHERE wb_id = ?
    """,
        (id_to_check,),
    )
    row = cursor.fetchone()
    return row if row else False


def get_post_status(id_to_check, table_name):
    cursor = connect_database(table_name).cursor()
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


def set_post_status(wb_id, status, table_name):
    connection = connect_database(table_name)
    cursor = connection.cursor()
    cursor.execute(
        f"""
    UPDATE {table_name} SET status = ? WHERE wb_id = ?
    """,
        (status, wb_id),
    )
    connection.commit()


def add_post(wb_id, table_name, status="Idle"):
    connection = connect_database(table_name)
    cursor = connection.cursor()
    cursor.execute(
        f"""
    INSERT INTO {table_name} (wb_id, status) VALUES (?, ?)
                   """,
        (wb_id, status),
    )
    connection.commit()


def get_all_posts(table_name):
    cursor = connect_database(table_name).cursor()
    cursor.execute(
        f"""
    SELECT wb_id FROM {table_name}
    """
    )
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    # result = [dict(zip(column_names, row)) for row in rows]
    res = [row[0] for row in rows]
    return res


def delete_all_records(table_name):
    connection = connect_database(table_name)
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM {table_name}")
    connection.commit()


def close_connection(table_name):
    connection = connect_database(table_name)
    connection.close()


if __name__ == "__main__":
    con = connect_database(db_file=r"sql_data\tp_tgwb.sqlite")
    print(get_all_posts(con))
