# -*- coding: utf-8 -*-

import json
from marshmallow import Schema, fields


class User(object):
    """
    Entity user
    """
    def __init__(self, id, name, email, password, role, created, idcreated):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.created = created
        self.idcreated = idcreated

    def __repr__(self):
        return '<User(name={self.name!r})>'.format(self=self)

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


class UserSchema(Schema):
    """
     User Schema
    """
    id = fields.String(required=False, description="user id")
    name = fields.String(required=True, description="user name")
    email = fields.String(required=True, description="user name")
    password = fields.String(required=True, description="user password")
    role = fields.String(required=True, description="user role")
    created = fields.String(required=False, description="user created date")
    idcreated = fields.String(required=False, description="user idcreated user")
