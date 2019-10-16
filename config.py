##Este es el archivo que contiene la importancia de clases y algunas configuraciones que tienen que ir en el main, esto con la finalidad de reducir codigo
import os
from models.Producto import Producto


class Config(object):
    SECRET_KEY = "my_secret_key"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/cania'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
