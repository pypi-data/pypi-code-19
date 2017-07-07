# -*- coding: utf-8 -*filter_dict = { 'description__contains': 'Oi', 'id__gte': 1 }-
from flask_sqlalchemy import Model, SQLAlchemy
from sqlalchemy import *

class FlaskPumpWoodBaseModel(Model):
    '''
        Flask Sqlalchemy Database Connection:
        - adds a id column for all models
        - implements save function facilitate model manipulaition
    '''
    id =  Column(Integer, primary_key=True)
    '''All tables must have primary id'''