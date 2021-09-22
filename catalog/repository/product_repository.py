# -*- coding: utf-8 -*-

from model.product import Product


class UserRepository(object):
    """
    User repository
    """
    def __init__(self, session):
        self.session = session

    def add(self, entity):
        """
         Add new entity
        :param entity: Product
        :return:
        """
        self.session.add(entity)
        self.session.commit()
        return entity

    def get_by_sku(self, sku):
        """
         Get product by sku
        :param sku: product sku
        :return: one product
        """
        return self.session.query(Product).filter_by(sku=sku).first()

    def get_all(self):
        """
        Get all product
        :return: List product in db
        """
        return self.session.query(Product).all()

    def update(self, entity):
        """
         Update entity
        :param entity: Product entity to update
        :return: True or False
        """
        self.session.add(entity)
        self.session.commit()
        return True

    def delete(self, sku):
        """
         Delete product by sku
        :param sku: product sku
        :return: True or False
        """
        entity = self.session.query(Product).filter_by(sku=sku).one()
        self.session.delete(entity)
        self.session.commit()
        return True
