# -*- coding: utf-8 -*-
import logging
import os
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import and_, or_
from Recognizer.utils.pre_start_init import paths
from Recognizer.models.db_models import Order, Recognitions
from Recognizer import LongTimeWorker

# import pymysql
from sqlalchemy import select, delete, create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, SmallInteger, Boolean, sql, func, update, desc

import config
from datetime import datetime, timedelta


class DataBase:
    def __init__(self):
        self.db_path = self.set_db_path()
        self.engine = create_engine(self.db_path, pool_pre_ping=True, json_serializer=True)
        self.session = Session(bind=self.engine)

    def set_db_path(self):
        db = 'sqlite:///' + str(paths.get("db"))
        if paths.get("db").exists():
            print(f'НУ В ЦЕЛОМ БД НА МЕСТЕ - {str(paths.get("db"))}')
            logging.error(f'НУ В ЦЕЛОМ БД НА МЕСТЕ - {str(paths.get("db"))}')
        else:
            print(f'БАЗЫ НЕТ ВОВСЕ! - {str(paths.get("db"))}')
            logging.error(f'БАЗЫ НЕТ ВОВСЕ! - {str(paths.get("db"))}')

        print(db)
        # db = 'mysql+pymysql://akojevnikov:zb5vdbpH0LL1Hxk8@192.168.94.61/kojevnikov_db'
        return db  # db

    async def add_order_to_base(self, data):
        with self.session as sess:
            u_id = data
            orders_data = LongTimeWorker.State.request_data[u_id]
            new_order = Order(
                u_id=u_id,
                erp_id=orders_data.get(""),
                file_url=orders_data.get("file_url").unicode_string(),
                state=orders_data.get("state"),
                inserted=datetime.now(),
                updated=datetime.now(),
            )

            user_exist = sess.query(Order).filter(Order.u_id == u_id)

            if sess.query(user_exist.exists()).scalar():
                user_exist.update(
                    {
                        'u_id': u_id,
                        'erp_id': orders_data.get(""),
                        'file_url': orders_data.get("file_url").unicode_string(),
                        'state': orders_data.get("state"),
                        'updated': datetime.now(),
                    },
                    synchronize_session='fetch')
            else:
                sess.add(new_order)
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
