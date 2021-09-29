# -*- coding: utf-8 -*-

import datetime
import uuid
import jwt

from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, snake_case_fallback_resolvers, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from graphql_operations.queries import listProducts_resolver, getProduct_resolver, getUser_resolver, listUsers_resolver
from graphql_operations.mutations import delete_product_resolver, login_resolver, IsAuthorizedDirective, \
    IsAuthenticatedDirective, add_product_resolver, update_product_resolver, add_user_resolver, update_user_resolver, \
    delete_user_resolver
from functools import wraps
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
        if 'X-Access-Token' in request.headers:
            token = request.headers['X-Access-Token']
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


query = ObjectType("Query")
mutation = ObjectType("Mutation")

query.set_field("listProducts", listProducts_resolver)
query.set_field("getProduct", getProduct_resolver)
query.set_field("listUsers", listUsers_resolver)
query.set_field("getUser", getUser_resolver)

mutation.set_field("login", login_resolver)
mutation.set_field("addProduct", add_product_resolver)
mutation.set_field("deleteProduct", delete_product_resolver)
mutation.set_field("updateProduct", update_product_resolver)
mutation.set_field("addUser", add_user_resolver)
mutation.set_field("updateUser", update_user_resolver)
mutation.set_field("deleteUser", delete_user_resolver)

type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(
    type_defs, query, mutation, snake_case_fallback_resolvers,
    directives={"isAuthorized": IsAuthorizedDirective, "isAuthenticated": IsAuthenticatedDirective}
)


@app.route('/')
def index():
    return 'Catalog API !!'


def get_user_context(request):
    """
     Get user context from request graphql
    :param request: request
    :return: dict context
    """
    context = {'request': request, 'user': None}
    if "Authorization" in request.headers:
        auth = request.headers["Authorization"]
        try:
            data = jwt.decode(auth, app.config['SECRET_KEY'], algorithms=["HS256"])
            session = Session()
            repository = UserRepository(session)
            current_user = repository.get_by_id(data['public_id'])
            # print(current_user)
            if current_user is None:
                return context
            else:
                context['user'] = current_user
        except jwt.PyJWTError:
            return context
    return context


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=get_user_context(request),
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code


### CORS section
@app.after_request
def after_request_func(response):
    origin = request.headers.get('Origin')
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', '*')       
        response.headers.add('Access-Control-Allow-Methods',
                            'GET, POST, OPTIONS, PUT, PATCH, DELETE')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)

    return response
    ### end CORS section


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

@app.route('/products/sku/<sku>', methods=['GET'])
@doc(description='GET Product API.', tags=['Product'])
@token_required
@use_kwargs({'sku': fields.Str()})
@marshal_with(ProductSchema)
def get_product_by_sku(current_user, sku):
    """
     Get all products
    :return: json all products
    """
    session = Session()
    repository = ProductRepository(session)
    product = repository.get_by_sku(sku)
    schema = ProductSchema(many=False)
    result_product = schema.dump(product)
    return jsonify(result_product)


@app.route('/products/name/<name>', methods=['GET'])
@doc(description='GET Product API.', tags=['Product'])
@token_required
@use_kwargs({'name': fields.Str()})
@marshal_with(ProductSchema)
def get_product_by_name(current_user, name):
    """
     Get all products
    :return: json all products
    """
    print('get_product_by_name {}'.format(name))
    session = Session()
    repository = ProductRepository(session)
    product = repository.get_by_name(name)
    print("Count all products {}".format(product.__len__()))
    schema = ProductSchema(many=True)
    result_product = schema.dump(product)
    return jsonify(result_product)


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
    return "Unauthorized user", 401

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
    print('Login')
    auth = request.authorization
    # print(request.authorization)
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
    # print(auth.username)
    session = Session()
    repository = UserRepository(session)
    users_db = repository.get_all()
    user = next((s for s in users_db if s.email == auth.username), None)
    if user is not None and check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'public_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},
            app.config['SECRET_KEY'])
        return jsonify({'token': token, 'user': user.to_json()})
    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

docs.register(get_product)
docs.register(post_product)
docs.register(put_product)
docs.register(delete_product)
docs.register(get_product_by_sku)
docs.register(get_product_by_name)

docs.register(get_user)
docs.register(post_user)
docs.register(put_user)
docs.register(delete_user)
docs.register(login_user)

if __name__ == '__main__':
    app.run(debug=True)