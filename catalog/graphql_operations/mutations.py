# -*- coding: utf-8 -*-

import jwt
import datetime
import uuid
import copy

from ariadne import convert_kwargs_to_snake_case
from ariadne import SchemaDirectiveVisitor
from graphql import  GraphQLError, default_field_resolver

from sqlalchemy.orm import sessionmaker, Session
from werkzeug.security import check_password_hash, generate_password_hash
from repository.product_repository import ProductRepository
from repository.user_repository import UserRepository
from sqlalchemy import create_engine
from model.product import Product
from model.user import User

engine = create_engine("sqlite:///catalog.db", connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)


class IsAuthorizedDirective(SchemaDirectiveVisitor):
    def visit_field_definition(self, field, object_type):
        print('visit_field_definition')
        original_resolver = field.resolve or default_field_resolver
        def resolve_is_authorized(obj, info, **kwargs):
            user = info.context.get('user')
            print(user)
            if user is None:
                raise GraphQLError(message="Not authenticated.")
            roles = self.args.get("roles")
            if roles is not None:
                if user.role not in roles:
                    raise GraphQLError(message="Not authorized.")
            result = original_resolver(obj, info, **kwargs)
            return result
        field.resolve = resolve_is_authorized
        return field


class IsAuthenticatedDirective(SchemaDirectiveVisitor):
    def visit_field_definition(self, field, object_type):
        original_resolver = field.resolve or default_field_resolver
        def resolve_is_authenticated(obj, info, **kwargs):
            user = info.context.get('user')
            if user is None:
                raise GraphQLError(message="Not authenticated.")
            result = original_resolver(obj, info, **kwargs)
            return result
        field.resolve = resolve_is_authenticated
        return field


@convert_kwargs_to_snake_case
def login_resolver(obj, info, username, password):
    """
     Login user
    :param obj:
    :param info:
    :param username: email user
    :param password: password user
    :return: token
    """
    try:
        if username is not None and password is not None:
            repository = UserRepository(Session())
            users_db = repository.get_all()
            user = next((s for s in users_db if s.email == username), None)
            if user is not None and check_password_hash(user.password, password):
                token = jwt.encode(
                    {'public_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},
                    'zaq1ZAQ2')
                payload = {"success": True, "token": token}
            else:
                payload = {"success": False, "token": "", "errors": ["Not found"]}
        else:
            payload = {"success": False, "token": "", "errors": ["Not found"]}
    except AttributeError:
        payload = {
            "success": False,
            "token": "",
            "errors": ["Not found"]
        }
    return payload


@convert_kwargs_to_snake_case
def add_product_resolver(obj, info, name, price, brand):
    """
     Add new product
    :param obj:
    :param info:
    :param name: name product
    :param price: price product
    :param brand: brand product
    :return: ProductResult
    """
    try:
        repository = ProductRepository(Session())
        new_product = Product(str(uuid.uuid4()), name, price, brand,
                              datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'))
        result_product = copy.deepcopy(new_product)
        result = repository.add(new_product)
        if result:
            print("Result {}".format(result))
            payload = {"success": True, "product": result_product}
        else:
            payload = {"success": False, "product": "", "errors": ["Not found"]}
    except AttributeError:
        payload = {
            "success": False,
            "product": "",
            "errors": ["Not found"]
        }
    return payload


@convert_kwargs_to_snake_case
def update_product_resolver(obj, info,sku, name, price, brand):
    """
     Update product
    :param obj:
    :param info:
    :param sku: sku product
    :param name: name product
    :param price: price product
    :param brand: brand product
    :return: ProductResult
    """
    try:
        repository = ProductRepository(Session())
        update_product = repository.get_by_sku(sku)
        if update_product is not None:
            update_product.name = name
            update_product.price = price
            update_product.brand = brand
            result_product = copy.deepcopy(update_product)
            result = repository.update(update_product)
            if result:
                if result:
                    print("Result {}".format(result))
                    payload = {"success": True, "product": result_product}
                    # todo Send email to others admin
                else:
                    payload = {"success": False, "product": "", "errors": ["Not found"]}
    except AttributeError:
        payload = {
            "success": False,
            "product": "",
            "errors": ["Not found"]
        }
    return payload


@convert_kwargs_to_snake_case
def delete_product_resolver(obj, info, sku):
    """
     Delete product by sky
    :param obj:
    :param info:
    :param sku: sku product
    :return: ProductResult
    """
    try:
        repository = ProductRepository(Session())
        prduct = repository.get_by_sku(sku)
        if prduct is not None:
            result = repository.delete(sku)
            if result:
                payload = {"success": True, "product": prduct}
            else:
                payload = {"success": False, "product": "", "errors": ["Not found"]}
        else:
            payload = {"success": False, "product": "", "errors": ["Not found"]}
    except AttributeError:
        payload = {
            "success": False,
            "product": "",
            "errors": ["Not found"]
        }
    return payload


@convert_kwargs_to_snake_case
def add_user_resolver(obj, info, email, name, password, role):
    """
     Add new user
    :param obj:
    :param info:
    :param email: user email
    :param name: user name
    :param password: user password
    :param role: user role
    :return: UsersResult
    """
    try:
        repository = UserRepository(Session())
        password = generate_password_hash(password, method='sha256')
        current_user = info.context.get('user')
        new_user = User(str(uuid.uuid4()), name, email, password, role,
                        datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'), current_user.id)
        result_user = copy.deepcopy(new_user)
        result = repository.add(new_user)
        if result:
            print("Result {}".format(result))
            payload = {"success": True, "user": result_user}
        else:
            payload = {"success": False, "user": "", "errors": ["Not found"]}
    except AttributeError:
        payload = {
            "success": False,
            "user": "",
            "errors": ["Not found"]
        }
    return payload


@convert_kwargs_to_snake_case
def update_user_resolver(obj, info, id, name, password, role):
    """
    Update user
    :param obj:
    :param info:
    :param id: id user
    :param name: name user
    :param password: password user
    :param role: role user
    :return: UsersResult
    """
    try:
        repository = UserRepository(Session())
        update_user = repository.get_by_id(id)
        if update_user is not None:
            password = generate_password_hash(password, method='sha256')
            update_user.name = name
            update_user.password = password
            update_user.role = role
            result_user = copy.deepcopy(update_user)
            result = repository.update(update_user)
            if result:
                if result:
                    print("Result {}".format(result))
                    payload = {"success": True, "user": result_user}
                else:
                    payload = {"success": False, "user": "", "errors": ["Not found"]}
    except AttributeError:
        payload = {
            "success": False,
            "user": "",
            "errors": ["Not found"]
        }
    return payload


@convert_kwargs_to_snake_case
def delete_user_resolver(obj, info, id):
    """
     Delete user by id
    :param obj:
    :param info:
    :param sku: id user
    :return: UsersResult
    """
    try:
        repository = UserRepository(Session())
        user = repository.get_by_id(id)
        if user is not None:
            result = repository.delete(id)
            if result:
                payload = {"success": True, "user": user}
            else:
                payload = {"success": False, "user": "", "errors": ["Not found"]}
        else:
            payload = {"success": False, "user": "", "errors": ["Not found"]}
    except AttributeError:
        payload = {
            "success": False,
            "user": "",
            "errors": ["Not found"]
        }
    return payload


