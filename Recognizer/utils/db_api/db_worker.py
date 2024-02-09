# -*- coding: utf-8 -*-
import os
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import and_, or_
from Recognizer.utils.pre_start_init import paths

# import pymysql
from sqlalchemy import select, delete, create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, SmallInteger, Boolean, sql, func, update, desc

import config
from Recognizer.models.db_models import Order, Recognitions
from datetime import datetime, timedelta


class DataBase:
    def __init__(self):
        self.db_path = self.set_db_path()
        self.engine = create_engine(self.db_path, pool_pre_ping=True, json_serializer=True)
        self.session = Session(bind=self.engine)

    def set_db_path(self):
        base_folder = os.getcwd()
        db = 'sqlite:///' + str(paths.get("db"))
        # db = 'mysql+pymysql://akojevnikov:zb5vdbpH0LL1Hxk8@192.168.94.61/kojevnikov_db'
        return base_folder  # db

    async def add_order_to_base(self, data):
        """ Мы получаем dict(data) {'login': 'login', 'password':'password', 'acc_t': 'token'} """
        # todo - проверить, есть ли супплаер с номером в базе по его token. Прекращать, если нет.
        with self.session as sess:
            data['inserted'] = datetime.now()
            data['next_check_date'] = datetime.now()
            data['auth_json_data'] = {
                "cookies": [
                    {
                        "name": "acc_t",
                        "value": data.get('acc_t'),
                        "domain": ".gosuslugi.ru",
                        "path": "/",
                        "expires": datetime.strptime(data.get('expire_at'), "%Y-%m-%d %H:%M:%S").timestamp(),
                        "httpOnly": False,
                        "secure": False,
                        "sameSite": "Lax"
                    },
                    {
                        "name": "u",
                        "value": data.get('oid'),
                        "domain": ".gosuslugi.ru",
                        "path": "/",
                        "expires": -1,
                        "httpOnly": False,
                        "secure": False,
                        "sameSite": "Lax"
                    },
                    {
                        "name": "ESIA_SESSION",
                        "value": "0e89acb6-b16c-e756-6f73-67d5ef708f21",
                        "domain": "esia.gosuslugi.ru",
                        "path": "/",
                        "expires": datetime.strptime(data.get('expire_at'), "%Y-%m-%d %H:%M:%S").timestamp(),
                        "httpOnly": True,
                        "secure": True,
                        "sameSite": "Lax"
                    },
                ],
                "origins": [
                ]
            }
            # Удаляем ключи, которых нет в модели Orders
            data.pop('acc_t', None)
            data.pop('expire_at', None)
            data.pop('oid', None)

            for sym in Order.items:
                data[sym] = data.get(sym, None)  # Если в ответе нет подходящего ключа, заменяем его на None
                order = Order(**data)
            sess.add(order)

            try:
                sess.commit()
                sess.close()
            except Exception as e:
                print(f'При добавлении Заказа возникла ошибка {e}')
                res = {
                    "state": False,
                    "Error": e[0:20]
                }
            else:
                print(f'Добавили заказ(ы) в базу')
                res = {
                    "state": True,
                    "Error": None
                }
        return res

    async def check_if_user_exists(self, user_id):
        with self.session as sess:
            user_exist = sess.query(Supplier).filter(Supplier.external_id == user_id).first()
        if user_exist:
            return user_exist
        else:
            return False

    async def find_user_by_lastname(self, client_lastname, suplier_id):
        with self.session as sess:

            user_data = dict()
            # print(user_lastname)
            try:
                q_user_data = sess.query(Client, Order). \
                    join(Order, isouter=True). \
                    join(Supplier, isouter=True).filter(
                    Client.lastName == client_lastname,
                    Supplier.external_id == suplier_id
                ).first()
                sess.close()
            except Exception as e:
                print(f'Произошла ошибка выбора Ордера для работы - {e}')
            else:
                if q_user_data:
                    user_data['lastname'] = q_user_data.Client.lastName
                    user_data['firstname'] = q_user_data.Client.firstName
                    user_data['started'] = q_user_data.Order.inserted
                    if q_user_data.Order.next_check_date:
                        user_data['next_check_date'] = q_user_data.Order.next_check_date
                    user_data['last_update_date'] = q_user_data.Order.next_check_date
                    user_data['state'] = q_user_data.Order.state
                    user_data['token'] = q_user_data.Order.token
                else:
                    user_data = False
        return user_data

    async def find_user_by_login(self, user_login):
        with self.session as sess:
            user_token = None
            # print(user_lastname)
            try:
                q_user_data = sess.query(Order). \
                    filter(Order.login == user_login).first()
                sess.close()
            except Exception as e:
                print(f'Произошла ошибка выбора Ордера для работы - {e}')
            else:
                if q_user_data:
                    user_token = q_user_data.token
                else:
                    user_token = None
        return user_token


db = DataBase()
