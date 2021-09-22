# -*- coding: utf-8 -*-

import sqlite3

from model.product import Product


def get_db():
    """
    Get conecct to db catalog
    :return:
    """
    conn = sqlite3.connect("catalog.db")
    return conn


def create_table():
    """
    Create table product to db
    :return:
    """
    tables = [
        """CREATE TABLE IF NOT EXISTS product(
                sku TEXT PRIMARY KEY,
                name TEXT NOT NULL,
				price REAL NOT NULL,
				brand TEXT NOT NULL,
				created TEXT NOT NULL
            )
            """
    ]
    db = get_db()
    cursor = db.cursor()
    for table in tables:
        cursor.execute(table)


def add_product(product):
    """
    Add product
    :param product: Entitu Product
    :return: True or False
    """
    db = get_db()
    cursor = db.cursor()
    statement = "INSERT INTO product(sku, name, price, brand, created) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(statement, [product.sku, product.name, product.price, product.brand, product.created])
    db.commit()
    return True


def get_all_product():
    """
    Get all product from table product
    :return: list product
    """
    db = get_db()
    cursor = db.cursor()
    query = "SELECT sku, name, price, brand, created FROM product"
    cursor.execute(query)
    all_products = cursor.fetchall()
    products = []
    for product in all_products:
        new_product = Product(product[0], product[1], product[2], product[3], product[4])
        products.append(new_product)
    # schema = ProductSchema(many=True)
    # all_product = schema.dump(products)
    return products


def get_product_by_sku(sku):
    """
    Get product by sku
    :param sku:
    :return:
    """
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT sku, name, price, brand, created FROM product WHERE sku = ?"
    cursor.execute(statement, [sku])
    product = cursor.fetchone()
    if product is not None:
        new_product = Product(product[0], product[1], product[2], product[3], product[4])
        return new_product
    return None


def update_product(product):
    """
    Update product
    :param product: Entity Product
    :return: True or false
    """
    db = get_db()
    cursor = db.cursor()
    statement = "UPDATE product SET name = ?, price = ?, brand = ?, created = ? WHERE sku = ?"
    cursor.execute(statement, [product.name, product.price, product.brand, product.created, product.sku])
    db.commit()
    return True


def delete_product(sku):
    """
    Delete product by sku
    :param sku: Sku product
    :return: True or False
    """
    db = get_db()
    cursor = db.cursor()
    statement = "DELETE FROM product WHERE sku = ?"
    cursor.execute(statement, [sku])
    db.commit()
    return True
