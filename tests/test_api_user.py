# -*- coding: utf-8 -*-

import datetime
import json
import uuid
import requests

from catalog.model.user import User, UserSchema


def test_get_user():
    """
     Test for get_user
    :return:
    """
    try:
        login = requests.post('http://127.0.0.1:5000/login', data={}, auth=('adminApi@gmail.com', 'zaq1ZAQ!'))
        if login.status_code == 200:
            token = login.json()['token']
            print(token)
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-tokens': token}
            response = requests.get('http://127.0.0.1:5000/user', headers=headers)
            assert response.status_code == 200
    except Exception as e:
        print(e)
        assert False


def test_add_user():
    """
     Test for add_user
    :return:
    """
    try:
        login = requests.post('http://127.0.0.1:5000/login', data={}, auth=('adminApi@gmail.com', 'zaq1ZAQ!'))
        # login = requests.post('http://127.0.0.1:5000/login', data={}, auth=('anonymousApi@gmail.com', '1qazxsw2'))
        if login.status_code == 200:
            token = login.json()['token']
            print(token)
            new_user = User("", "admin2", "admin2Api@gmail.com", '1qazxsw2', 'Admin',
                              datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'), '')
            json_string = new_user.to_json()
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-tokens': token }
            response = requests.post('http://127.0.0.1:5000/user', data=json_string, headers=headers)
            assert response.status_code == 200
    except Exception as e:
        print(e)
        assert False


def test_update_user():
    """
    Test for update_user
    :return:
    """
    try:
        login = requests.post('http://127.0.0.1:5000/login', data={}, auth=('adminApi@gmail.com', 'zaq1ZAQ!'))
        if login.status_code == 200:
            token = login.json()['token']
            print(token)
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-tokens': token}
            users = requests.get('http://127.0.0.1:5000/user', headers=headers)
            schema = UserSchema(many=True)
            all_user = schema.loads(users.text)
            user_update = all_user[3]
            user = User(user_update['id'], user_update['name'], user_update['email'],
                        user_update['password'], user_update['role'], user_update['created'], user_update['idcreated'])
            user['name'] = 'Test test'
            json_string = user.to_json()
            response = requests.put('http://127.0.0.1:5000/user', data=json_string, headers=headers)
            assert response.status_code == 200
    except Exception as e:
        print(e)
        assert False


def test_delete_user():
    """
    Test for delete_user
    :return:
    """
    try:
        login = requests.post('http://127.0.0.1:5000/login', data={}, auth=('adminApi@gmail.com', 'zaq1ZAQ!'))
        if login.status_code == 200:
            token = login.json()['token']
            print(token)
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-tokens': token}
            users = requests.get('http://127.0.0.1:5000/user', headers=headers)
            json_data = json.loads(users.text)
            id_user = json_data[3]['id']
            delete = requests.delete('http://127.0.0.1:5000/user/{}'.format(id_user), headers=headers)
            assert delete.status_code == 200
    except Exception as e:
        print(e)
        assert False
