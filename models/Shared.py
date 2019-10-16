from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cania'  # conexion con la base de datos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Cosa extra para evitar notificaciones
db = SQLAlchemy(app)
