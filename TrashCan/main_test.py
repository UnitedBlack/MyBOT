from sql_data import posts_sql, products_sql
from pprint import pprint


def wbparse():
    all_products = products_sql.get_all_products("tp_wb")

    tg_posts = posts_sql.get_all_posts("tp_tg")
    filtered_products = [
        product for product in all_products if product["url"] not in tg_posts
    ]
    for products in filtered_products:
        yield products


# def zaloo():
#     a = True
#     parser_data = wbparse()
#     for data in parser_data:
#         print(data)
#         a = False


parsed_data = wbparse()
print(next(parsed_data))
print(next(parsed_data))
print(next(parsed_data))
