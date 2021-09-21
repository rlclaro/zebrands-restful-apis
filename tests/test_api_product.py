# -*- coding: utf-8 -*-

import datetime
import json
import uuid
import requests

from catalog.model.product import Product, ProductSchema


def test_get_products():
    """
     Test for get_products
    :return:
    """
    try:
        products = requests.get('http://127.0.0.1:5000/products')
        assert products.status_code == 200
    except Exception as e:
        print(e)
        assert False


def test_add_product():
    """
     Test for add_product
    :return:
    """
    try:
        login = requests.post('http://127.0.0.1:5000/login', data={}, auth=('adminApi@gmail.com', 'zaq1ZAQ!'))
        # login = requests.post('http://127.0.0.1:5000/login', data={}, auth=('anonymousApi@gmail.com', '1qazxsw2'))
        if login.status_code == 200:
            token = login.json()['token']
            print(token)
            data = Product(uuid.uuid4().__str__(), 'Silla', 50, 'Luuna',
                           datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'))
            json_string = data.to_json()

            date_str = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S').__str__()
            date_format = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
            print(date_format)

            headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-tokens': token}
            response = requests.post('http://127.0.0.1:5000/products', data=json_string, headers=headers)
            assert response.status_code == 200
    except Exception as e:
        print(e)
        assert False


def test_update_product():
    """
     Test for update_product
    :return:
    """
    try:
        products = requests.get('http://127.0.0.1:5000/products')
        login = requests.post('http://127.0.0.1:5000/login', data={}, auth=('adminApi@gmail.com', 'zaq1ZAQ!'))
        if products.status_code == 200 and login.status_code == 200:
            token = login.json()['token']
            print(token)
            schema = ProductSchema(many=True)
            all_product = schema.loads(products.text)
            product_update = all_product[0]
            product = Product(product_update['sku'], product_update['name'], product_update['price'],
                              product_update['brand'], product_update['created'])
            product['price'] = 1000
            json_string = product.to_json()
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-tokens': token}
            response = requests.put('http://127.0.0.1:5000/products', data=json_string, headers=headers)
            assert response.status_code == 200
    except Exception as e:
        print(e)
        assert False


def test_delete_products():
    """
    Test for delete_products
    :return:
    """
    try:
        products = requests.get('http://127.0.0.1:5000/products')
        login = requests.post('http://127.0.0.1:5000/login', data={}, auth=('adminApi@gmail.com', 'zaq1ZAQ!'))
        if products.status_code == 200 and login.status_code == 200:
            token = login.json()['token']
            print(token)
            json_data = json.loads(products.text)
            first_sku = json_data[0]['sku']
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-tokens': token}
            response = requests.delete('http://127.0.0.1:5000/products/{}'.format(first_sku), headers=headers)
            assert response.status_code == 200
    except Exception as e:
        print(e)
        assert False
