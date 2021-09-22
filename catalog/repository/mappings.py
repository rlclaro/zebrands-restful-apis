# -*- coding: utf-8 -*-

from sqlalchemy import MetaData, Table, String, Column, Integer
from sqlalchemy.orm import mapper
from model.product import Product

metadata = MetaData()

product = Table('post', metadata,
    Column('sku', String(), primary_key=True),
    Column('name', String(), nullable= False),
    Column('price', Integer(), nullable= False),
    Column('brand', String(), nullable= False),
    Column('created', String(), nullable= False)
)

mapper(Product, product)