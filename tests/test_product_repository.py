# -*- coding: utf-8 -*-

import uuid
import datetime

from product_repository import create_table, add_product, get_all_product, delete_product
from catalog.model.product import Product

def test_create_table():
    """
    Test for create_tables
    :return: assert True or False
    """
    try:
        create_table()
        assert True
    except Exception as e:
        print(e)
        assert False

def test_add_product():
    """
    Test for add_product
    :return: assert True or False
    """
    try:
        products = [
            Product(uuid.uuid4().__str__(), 'Colchones', 500, 'Luuna',
                    datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')),
            Product(uuid.uuid4().__str__(), 'Camas', 400, 'Luuna',
                    datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')),
            Product(uuid.uuid4().__str__(), 'Muebles', 800, 'Luuna',
                    datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')),
            Product(uuid.uuid4().__str__(), 'Almohadas', 100, 'Luuna',
                    datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'))
        ]
        count = 0
        for product in products:
            result = add_product(product)
            if result:
                count +=1
        assert count == 4
    except Exception as e:
        print(e)
        assert False

def test_get_all_product():
    """
    Test for get_all_product
    :return: assert True or False
    """
    try:
        products_db = get_all_product()
        assert products_db.__len__() > 0
    except Exception as e:
        print(e)
        assert False

def test_delete_product():
    """
    Test for delete_product
    :return: assert True or False
    """
    try:
        deleted = delete_product('57eb4f8c-ba02-41e1-abc7-56958b8c158e')
        assert deleted == True
    except Exception as e:
        print(e)
        assert False
