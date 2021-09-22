# -*- coding: utf-8 -*-

import json

from marshmallow import Schema, fields


class Product(object):
    """
     Entity product
    """
    def __init__(self, sku, name, price, brand, created):
        self.sku = sku
        self.name = name
        self.price = price
        self.brand = brand
        self.created = created

    def __repr__(self):
        return '<Product(name={self.name!r})>'.format(self=self)

    @classmethod
    def from_json(cls, json_str):
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, dict_obj):
        return cls(**dict_obj)

    def set_attr(self, name, value):
        setattr(self, name, value)

    def set_attrs(self, entity_dict):
        for k in entity_dict.keys():
            self.set_attr(k, entity_dict[k])

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        self.set_attr(key, value)

    def to_json(self):
        return json.dumps(self.__dict__, default=str)

    def to_dict(self):
        return json.loads(self.to_json())


class ProductSchema(Schema):
    """
    Product Schema
    """
    sku = fields.String(required=False, description="product sku")
    name = fields.String(required=True, description="product name")
    price = fields.Integer(required=True, description="product price")
    brand = fields.String(required=True, description="product brand")
    created = fields.String(required=True, description="product created")


class EmptySchema(Schema):
    pass