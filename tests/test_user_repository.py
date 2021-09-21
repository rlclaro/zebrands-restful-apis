# -*- coding: utf-8 -*-

import uuid
import datetime

from user_repository import create_table, add_user, get_all_user, delete_user, get_user_by_id
from catalog.model.user import User
from werkzeug.security import generate_password_hash

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

def test_add_user():
    """
    Test for add_user
    :return: assert True or False
    """
    try:
       users_db = get_all_user()
       exists_admin_api = next((s for s in users_db if s.email == 'adminApi@gmail.com'), None)
       if exists_admin_api is None:
           id_admin = str(uuid.uuid4())
           password = generate_password_hash('zaq1ZAQ!', method='sha256')
           admin_user = User(id_admin, "admin", "adminApi@gmail.com", password, 'Admin',
                             datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'), id_admin)
           exist_admin = get_user_by_id(id_admin)
           if exist_admin is None:
               new_admin = add_user(admin_user)
               print("New admin {}".format(new_admin))
       exists_admin_api = next((s for s in users_db if s.email == 'adminApi@gmail.com'), None)
       exists_anonymous_api = next((s for s in users_db if s.email == 'anonymousApi@gmail.com'), None)
       if exists_admin_api is not None and exists_anonymous_api is None:
           id_anonymous = str(uuid.uuid4())
           password = generate_password_hash('1qazxsw2', method='sha256')
           anonymous_user = User(id_anonymous, "anonymous", "anonymousApi@gmail.com", password, 'Anonymous',
                                 datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'), exists_admin_api.id)
           exist_anonymous = get_user_by_id(id_anonymous)
           if exist_anonymous is None:
               new_anonymous = add_user(anonymous_user)
               print("New anonymous {}".format(new_anonymous))
       assert True
    except Exception as e:
        print(e)
        assert False

def test_get_all_user():
    """
    Test for get_all_user
    :return:assert True or False
    """
    try:
        users_db = get_all_user()
        assert users_db.__len__() > 0
    except Exception as e:
        print(e)
        assert False

def test_delete_user():
    """
    Test for delete_user
    :return: assert True or False
    """
    try:
        deleted = delete_user('57eb4f8c-ba02-41e1-abc7-56958b8c158e')
        assert deleted == True
    except Exception as e:
        print(e)
        assert False
