# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from ariadne import convert_kwargs_to_snake_case
from sqlalchemy.orm import sessionmaker, Session
from repository.product_repository import ProductRepository
from repository.user_repository import UserRepository

engine = create_engine("sqlite:///catalog.db", connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)


def listProducts_resolver(obj, info):
    """
    List products
    :param obj:
    :param info:
    :return: List entity product
    """
    try:
        repository = ProductRepository(Session())
        products = repository.get_all()
        # print(products)
        payload = {
            "success": True,
            "product": products
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload


def listUsers_resolver(obj, info):
    """
    List user
    :param obj:
    :param info:
    :return: List entity user
    """
    try:
        repository = UserRepository(Session())
        users = repository.get_all()
        payload = {
            "success": True,
            "user": users
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload


@convert_kwargs_to_snake_case
def getProduct_resolver(obj, info, sku):
    """
     Get product by sku
    :param obj:
    :param info:
    :param sku: sku product
    :return: Entity product
    """
    try:
        repository = ProductRepository(Session())
        print(sku)
        product = repository.get_by_sku(sku)
        payload = {
            "success": True,
            "product": product
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Todo item matching id {sku} not found"]
        }
    return payload


@convert_kwargs_to_snake_case
def getUser_resolver(obj, info, username):
    """
     Get user by email
    :param obj:
    :param info:
    :param username: email user
    :return: Entity User
    """
    try:
        repository = UserRepository(Session())
        user = repository.get_by_email(username)
        payload = {
            "success": True,
            "user": user
        }
    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Todo item matching username {username} not found"]
        }
    return payload

