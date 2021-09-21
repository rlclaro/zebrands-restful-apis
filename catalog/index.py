# -*- coding: utf-8 -*-

import product_repository
import user_repository
import jwt
import uuid
import datetime

from flask import Flask, jsonify, request, make_response
from model.product import ProductSchema, Product
from model.user import UserSchema, User
from functools import wraps
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask_mail import Mail, Message


app = Flask(__name__)
app.config['SECRET_KEY'] = 'zaq1ZAQ2'
mail = Mail(app)


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
            current_user = user_repository.get_user_by_id(data['public_id'])
        except Exception as e:
            print("Error in decorator {}".format(e.__str__()))
            return jsonify({'message': 'token is invalid'})
        return f(current_user, *args, **kwargs)
    return decorator


@app.route('/products')
def get_products():
    """
     Get all products
    :return: json all products
    """
    schema = ProductSchema(many=True)
    products = product_repository.get_all_product()
    print("Count all products {}".format(products.__len__()))
    all_product = schema.dump(products)
    return jsonify(all_product)


@app.route('/products', methods=['POST'])
@token_required
def add_product(current_user):
    """
     Add new product
    :param current_user: current user from jwt
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        product = ProductSchema().load(request.get_json())
        new_product = Product(product['sku'], product['name'], product['price'], product['brand'], product['created'])
        result = product_repository.add_product(new_product)
        if result:
            return "Product add OK", 200
        else:
            return "Error add new product", 400
    else:
        return "Unauthorized user ", 401


@app.route("/products", methods=["PUT"])
@token_required
def update_product(current_user):
    """
     Update product
     :param current_user: current user from jwt
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        product = ProductSchema().load(request.get_json())
        update_product = Product(product['sku'], product['name'], product['price'], product['brand'], product['created'])
        result = product_repository.update_product(update_product)
        if result:
            print("Update product {}".format(result))
            # send email to others Admin
            users = user_repository.get_all_user()
            with mail.connect() as conn:
               # print("Count user {}".format(users.__len__()))
                for user in users:
                    # print("Id {} current {} role {}".format(user.id, current_user.id, user.role))
                    if user.id != current_user.id and user.role == 'Admin':
                        # print("Send to user {}".format(user.email))
                        message = "Hello {} the product {} changed".format(user.name, update_product.sku)
                        subject = "Product change"
                        msg = Message(recipients=[user.email],
                                      sender= current_user.email,
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
def delete_product(current_user, sku):
    """
     Delete product
    :param current_user: current user from jwt
    :param sku: sku product
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        print("Sku delete {}".format(sku))
        result = product_repository.delete_product(sku)
        if result:
            return "Product delete OK", 200
        else:
            return "Error delete product", 400
    else:
        return "Unauthorized user ", 401


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """
    Login user in api
    :return: token
    """
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
    users_db = user_repository.get_all_user()
    user = next((s for s in users_db if s.email == auth.username), None)
    if user is not None and check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'public_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},
            app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})


@app.route('/user')
@token_required
def get_user(current_user):
    """
    Get all user
    :return: json all user
    """
    if current_user is not None and current_user.role == 'Admin':
        schema = UserSchema(many=True)
        users = user_repository.get_all_user()
        print("Count all users {}".format(users.__len__()))
        all_user = schema.dump(users)
        return jsonify(all_user)
    return "Unauthorized user ", 401


@app.route('/user', methods=['POST'])
@token_required
def add_user(current_user):
    """
    Add new user
    :param current_user: current user from jwt
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        user = UserSchema().load(request.get_json())
        password = generate_password_hash(user['password'], method='sha256')
        new_user = User(str(uuid.uuid4()), user['name'], user['email'], password, user['role'],
                        datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'), current_user.id)
        users_db = user_repository.get_all_user()
        exists_admin_api = next((s for s in users_db if s.email == new_user.email), None)
        if exists_admin_api is None:
            result = user_repository.add_user(new_user)
            if result:
                return "User add OK", 200
        return "Error add new user", 400
    else:
        return "Unauthorized user ", 401


@app.route("/user", methods=["PUT"])
@token_required
def update_user(current_user):
    """
     Update user
    :param current_user: current user from jwt
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        user = UserSchema().load(request.get_json())
        update_user = User(user['id'], user['name'], user['email'], user['password'], user['role'],
                           user['created'], user['idcreated'])
        result = user_repository.update_user(update_user)
        if result:
            return "Product update OK", 200
        else:
            return "Error update product", 400
    else:
        return "Unauthorized user ", 401


@app.route('/user/<id>', methods=['DELETE'])
@token_required
def delete_user(current_user, id):
    """
     Delete user by id
    :param current_user: current user from jwt
    :param id: id user
    :return: api result
    """
    if current_user is not None and current_user.role == 'Admin':
        print("Id delete {}".format(id))
        result = user_repository.delete_user(id)
        if result:
            return "Product delete OK", 200
        else:
            return "Error delete product", 400
    else:
        return "Unauthorized user ", 401


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
    response.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
    return response

if __name__ == "__main__":
    app.run()
