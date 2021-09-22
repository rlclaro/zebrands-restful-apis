# -*- coding: utf-8 -*-

from sqlalchemy import MetaData, Table, String, Column, Integer
from sqlalchemy.orm import mapper
from model.product import Product
from model.user import User

metadata = MetaData()

product = Table('product', metadata,
                Column('sku', String(), primary_key=True),
                Column('name', String(), nullable=False),
                Column('price', Integer(), nullable=False),
                Column('brand', String(), nullable=False),
                Column('created', String(), nullable=False)
                )

user = Table('user', metadata,
             Column('id', String(), primary_key=True),
             Column('name', String(), nullable=False),
             Column('email', String(), nullable=False),
             Column('password', String(), nullable=False),
             Column('role', String(), nullable=False),
             Column('created', String(), nullable=False),
             Column('idcreated', String(), nullable=False)
             )


def start_mappers():
    mapper(Product, product)
    mapper(User, user)
