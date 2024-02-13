import sqlalchemy as sa
import sqlalchemy_utils as su
import uuid


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy_utils import UUIDType
Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    u_id = sa.Column(su.UUIDType(binary=False), default=uuid.uuid4)
    erp_id = sa.Column(sa.String(9), default=None)
    file_url = sa.Column(su.URLType, default=None)
    state = sa.Column(sa.String(15), default='New')  # New, inwork, completed
    inserted = sa.Column(sa.DateTime, default=datetime.now())
    updated = sa.Column(sa.DateTime, default=datetime.now())
    items = [k for k in locals().keys() if not k.startswith('_')]  # для перебора переменных класса


class Recognitions(Base):
    __tablename__ = 'recognitions'
    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    orderID = sa.Column(sa.Integer, sa.ForeignKey('orders.id'))  # Внешник
    model = sa.Column(sa.String(30), default=None)
    json_raw = sa.Column(sa.Text, default=None)
    recognised_text = sa.Column(sa.Text, default=None)
    punctuated_text = sa.Column(sa.Text, default=None)
    json_dialogue = sa.Column(su.JSONType, default=None)
    last_update_date = sa.Column(sa.DateTime, default=datetime.now())
    items = [k for k in locals().keys() if not k.startswith('_')]  # для перебора переменных класса

# class Supplier(Base):
#     __tablename__ = 'suppliers'
#     id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
#     name = sa.Column(sa.String(40), default=None)  # "КЛИНКОВ"
#     token = sa.Column(su.UUIDType(binary=False), default=uuid.uuid4)
#     token_valid_until = sa.Column(sa.DateTime, default=None)
#     updated = sa.Column(sa.DateTime, default=datetime.now())
#     inserted = sa.Column(sa.DateTime, default=datetime.now())
#     state = sa.Column(sa.String(15), default="New")  # Blocked/Active
#     external_id = sa.Column(sa.String(40), default=None)
#     items = [k for k in locals().keys() if not k.startswith('_')]  # для перебора переменных класса