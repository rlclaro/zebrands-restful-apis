# -*- coding: utf-8 -*-

import datetime
import uuid
from functools import wraps

import jwt
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask
from flask import jsonify, request, make_response
from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec.extension import FlaskApiSpec
from flask_mail import Mail, Message
from flask_restful import Api
from marshmallow import fields
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from werkzeug.security import check_password_hash, generate_password_hash

from model.product import ProductSchema, Product, EmptySchema, AddProductSchema
from model.user import UserSchema, User, AddUserSchema
from repository.mappings import start_mappers
from repository.product_repository import ProductRepository
from repository.user_repository import UserRepository

app = Flask(__name__)  # Flask app instance initiated
api = Api(app)  # Flask restful wraps Flask app around it.
app.config['SECRET_KEY'] = 'zaq1ZAQ2'
mail = Mail(app)
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Catalog Restful Api',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

start_mappers()
engine = create_engine("sqlite:///catalog.db", connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)


def token_required(f):
    """
    Token request
    :param f:
    :return: user
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            # print("Token: {}".format(token))
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # print("Id User {}".format(data['public_id']))
            session = Session()
            repository = UserRepository(session)
            current_user = repository.get_by_id(data['public_id'])
            print(current_user)
        except Exception as e:
            print("Error in decorator {}".format(e.__str__()))
            return jsonify({'message': 'token is invalid'})
        return f(current_user, *args, **kwargs)

    return decorator


@app.after_request
def after_request(response):
    """
     Enable CORS. Disable it if you don't need CORS
    :param response:
    :return:
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response.headers[
        "Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
    return response


@app.route('/products', methods=['GET'])
@doc(description='GET Product API.', tags=['Product'])
@marshal_with(ProductSchema)
def get_product():
    """
     Get all products
    :return: json all products
    """
    session = Session()
    repository = ProductRepository(session)
    products = repository.get_all()
    schema = ProductSchema(many=True)
    print("Count all products {}".format(products.__len__()))
    all_product = schema.dump(products)
    return jsonify(all_product)

@app.route('/products', methods=['POST'])
@token_required
@doc(description='POST Product API.', tags=['Product'])
@use_kwargs(AddProductSchema, location=('json'))
@marshal_with(EmptySchema, code=200)
def post_product(current_user,  **kwargs):
    """
     Add new product
    :param current_user: current user from jwt
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        # print(request.get_json())
        product = AddProductSchema().load(request.get_json())
        new_product = Product(str(uuid.uuid4()), product['name'], product['price'], product['brand'],
                              datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'))
        session = Session()
        repository = ProductRepository(session)
        result = repository.add(new_product)
        if result:
            return "Product add OK", 200
        else:
            return "Error add new product", 400
    else:
        return "Unauthorized user ", 401


@app.route("/products", methods=["PUT"])
@token_required
@doc(description='PUT Product API.', tags=['Product'])
@use_kwargs(ProductSchema, location=('json'))
@marshal_with(EmptySchema, code=200)
def put_product(current_user, **kwargs):
    """
    Update product
    :param current_user: current user from jwt
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        product = ProductSchema().load(request.get_json())
        update_product = Product(product['sku'], product['name'], product['price'], product['brand'],
                                 product['created'])
        session = Session()
        repository = ProductRepository(session)
        result = repository.update(update_product)
        if result:
            print("Update product {}".format(result))
            # send email to others Admin
            session = Session()
            repository_user = UserRepository(session)
            users = repository_user.get_all()
            with mail.connect() as conn:
                # print("Count user {}".format(users.__len__()))
                for user in users:
                    # print("Id {} current {} role {}".format(user.id, current_user.id, user.role))
                    if user.id != current_user.id and user.role == 'Admin':
                        # print("Send to user {}".format(user.email))
                        message = "Hello {} the product {} changed".format(user.name, update_product.sku)
                        subject = "Product change"
                        msg = Message(recipients=[user.email],
                                      sender=current_user.email,
                                      body=message,
                                      subject=subject)
                        conn.send(msg)
                    # print('Send {}'.format(message))
            return "Product update OK", 200
        else:
            return "Error update product", 400
    else:
        return "Unauthorized user ", 401


@app.route('/products/<sku>', methods=['DELETE'])
@token_required
@doc(description='DELETE Product API.', tags=['Product'])
@use_kwargs({'sku': fields.Str()})
@marshal_with(EmptySchema, code=200)
def delete_product(current_user, sku):
    """
     Delete product
    :param current_user: current user from jwt
    :param sku: sku product
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        print("Sku delete {}".format(sku))
        session = Session()
        repository = ProductRepository(session)
        result = repository.delete(sku)
        if result:
            return "Product delete OK", 200
        else:
            return "Error delete product", 400
    else:
        return "Unauthorized user ", 401


@app.route('/user', methods=['GET'])
@token_required
@doc(description='GET User API.', tags=['User'])
@marshal_with(UserSchema(many=True))
def get_user(current_user):
    """
    Get all user
    :return: json all user
    """
    if current_user is not None and current_user.role == 'Admin':
        schema = UserSchema(many=True)
        session = Session()
        repository = UserRepository(session)
        users = repository.get_all()
        print("Count all users {}".format(users.__len__()))
        all_user = schema.dump(users)
        return jsonify(all_user)
    return "Unauthorized user ", 401

@app.route('/user', methods=['POST'])
@token_required
@doc(description='POST User API.', tags=['User'])
@use_kwargs(AddUserSchema, location=('json'))
@marshal_with(EmptySchema, code=200)
def post_user(current_user, **kwargs):
    """
    Add new user
    :param current_user: current user from jwt
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        user = AddUserSchema().load(request.get_json())
        password = generate_password_hash(user['password'], method='sha256')
        new_user = User(str(uuid.uuid4()), user['name'], user['email'], password, user['role'],
                        datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'), current_user.id)
        session = Session()
        repository = UserRepository(session)
        users_db = repository.get_all()
        exists_admin_api = next((s for s in users_db if s.email == new_user.email), None)
        if exists_admin_api is None:
            result = repository.add(new_user)
            if result:
                return "User add OK", 200
        return "Error add new user", 400
    else:
        return "Unauthorized user ", 401

@app.route("/user", methods=["PUT"])
@token_required
@doc(description='PUT User API.', tags=['User'])
@use_kwargs(UserSchema, location=('json'))
@marshal_with(EmptySchema, code=200)
def put_user(current_user, **kwargs):
    """
     Update user
    :param current_user: current user from jwt
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        user = UserSchema().load(request.get_json())
        update_user = User(user['id'], user['name'], user['email'], user['password'], user['role'],
                           user['created'], user['idcreated'])
        session = Session()
        repository = UserRepository(session)
        result = repository.update(update_user)
        if result:
            return "Product update OK", 200
        else:
            return "Error update product", 400
    else:
        return "Unauthorized user ", 401

@app.route('/user/<id>', methods=['DELETE'])
@token_required
@doc(description='DELETE User API.', tags=['User'])
@use_kwargs({'id': fields.Str()})
@marshal_with(EmptySchema, code=200)
def delete_user(current_user, id):
    """
     Delete user by id
    :param current_user: current user from jwt
    :param id: id user
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        print("Id delete {}".format(id))
        session = Session()
        repository = UserRepository(session)
        result = repository.delete(id)
        if result:
            return "Product delete OK", 200
        else:
            return "Error delete product", 400
    else:
        return "Unauthorized user ", 401


@app.route('/login', methods=['GET', 'POST'])
@doc(description='GET User API.', tags=['Login'])
@marshal_with(EmptySchema, code=200)
def login_user():
    """
    Login user in api
    :return: token
    """
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
    session = Session()
    repository = UserRepository(session)
    users_db = repository.get_all()
    user = next((s for s in users_db if s.email == auth.username), None)
    if user is not None and check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'public_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},
            app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

docs.register(get_product)
docs.register(post_product)
docs.register(put_product)
docs.register(delete_product)

docs.register(get_user)
docs.register(post_user)
docs.register(put_user)
docs.register(delete_user)
docs.register(login_user)

if __name__ == '__main__':
    app.run(debug=True)