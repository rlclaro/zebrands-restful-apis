# -*- coding: utf-8 -*-

from model.product import Product


class ProductRepository(object):
    """
    Product repository
    """

    def __init__(self, session):
        self.session = session

    def add(self, entity):
        """
         Add new entity
        :param entity: Product
        :return: True
        """
        self.session.add(entity)
        self.session.commit()
        #self.session.expunge_all()
        return True

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
        try:
            # print("Sku: {}".format(entity.sku))
            self.session.query(Product).filter_by(sku=entity.sku).update(
                {'name': entity.name, 'price': entity.price, "brand": entity.brand})
            self.session.commit()
            return True
        except:
            self.session.rollback()
            raise

    def delete(self, sku):
        """
         Delete product by sku
        :param sku: product sku
        :return: True or False
        """
        try:
            entity = self.session.query(Product).filter_by(sku=sku).one()
            self.session.delete(entity)
            self.session.commit()
            return True
        except:
            self.session.rollback()
            raise
