# -*- coding: utf-8 -*-

from model.user import User


class UserRepository(object):
    """
    User repository
    """
    def __init__(self, session):
        self.session = session

    def add(self, entity):
        """
         Add new entity
        :param entity: User
        :return: True
        """
        self.session.add(entity)
        self.session.commit()
        return True

    def get_by_id(self, id):
        """
         Get user by id
        :param id: User id
        :return: one User
        """
        return self.session.query(User).filter_by(id=id).first()

    def get_by_email(self, email):
        """
         Get user by email
        :param id: User email
        :return: one User
        """
        return self.session.query(User).filter_by(email=email).first()

    def get_all(self):
        """
        Get all User
        :return: List user in db
        """
        return self.session.query(User).all()

    def update(self, entity):
        """
         Update entity
        :param entity: User entity to update
        :return: True or False
        """
        try:
            # print("Id: {}".format(entity.id))
            self.session.query(User).filter_by(id=entity.id).update(
                {'name': entity.name, 'role': entity.role})
            self.session.commit()
            return True
        except:
            self.session.rollback()
            raise

    def delete(self, id):
        """
         Delete User by id
        :param id: User id
        :return: True or False
        """
        try:
            entity = self.session.query(User).filter_by(id=id).one()
            self.session.delete(entity)
            self.session.commit()
            return True
        except:
            self.session.rollback()
            raise
