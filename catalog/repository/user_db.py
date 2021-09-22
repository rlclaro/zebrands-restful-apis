# -*- coding: utf-8 -*-

import sqlite3

from model.user import User


def get_db():
    """
    Get conecct to db catalog
    :return:
    """
    conn = sqlite3.connect("../catalog.db")
    return conn


def create_table():
    """
    Create table user to db
    :return:
    """
    tables = [
        """CREATE TABLE IF NOT EXISTS user(
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
				email TEXT NOT NULL,
				password TEXT NOT NULL,
				role TEXT NOT NULL,
				created TEXT NOT NULL,
				idcreated TEXT NOT NULL			
            )
            """
    ]
    db = get_db()
    cursor = db.cursor()
    for table in tables:
        cursor.execute(table)


def add_user(user):
    """
    Add user
    :param user: Entitu User
    :return: True or False
    """
    db = get_db()
    cursor = db.cursor()
    statement = "INSERT INTO user(id, name, email, password, role, created, idcreated) VALUES (?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(statement, [user.id, user.name, user.email, user.password, user.role, user.created, user.idcreated])
    db.commit()
    return True


def get_all_user():
    """
    Get all user from table user
    :return: list user
    """
    db = get_db()
    cursor = db.cursor()
    query = "SELECT id, name, email, password, role, created, idcreated FROM user"
    cursor.execute(query)
    all_user = cursor.fetchall()
    users = []
    for item in all_user:
        new_user = User(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
        users.append(new_user)
    return users


def get_user_by_id(id):
    """
    Get user by id
    :param id:
    :return: User entity
    """
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT id, name, email, password, role, created, idcreated FROM user WHERE id = ?"
    cursor.execute(statement, [id])
    item = cursor.fetchone()
    if item is not None:
        new_user = User(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
        return new_user
    return None


def update_user(user):
    """
    Update user
    :param user: Entity User
    :return: True or false
    """
    db = get_db()
    cursor = db.cursor()
    statement = "UPDATE user SET name = ?, email = ?, password = ?, role = ?, created = ?, idcreated = ? WHERE id = ?"
    cursor.execute(statement, [user.name, user.email, user.password, user.role, user.created, user.idcreated, user.id])
    db.commit()
    return True


def delete_user(id):
    """
    Delete user by id
    :param id: Id User
    :return: True or False
    """
    db = get_db()
    cursor = db.cursor()
    statement = "DELETE FROM user WHERE id = ?"
    cursor.execute(statement, [id])
    db.commit()
    return True
