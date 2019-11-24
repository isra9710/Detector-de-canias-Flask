from sqlalchemy.orm import relationship
from models.Shared import db
from datetime import date

class Resultado(db.Model):
    __tablename__ = 'Resultado'
    idResultado = db.Column(db.Integer, primary_key=True)
    idUsuario = db.Column('idUsuario', db.Integer, db.ForeignKey("Usuario.idUsuario"))
    idP = db.Column('idP', db.Integer, db.ForeignKey("Producto.idP"))
    fecha = db.Column(db.Date,default=date.today)
    longitud = db.Column(db.Float)
    anchura = db.Column(db.Float)
    rojo = db.Column(db.Integer)
    verde = db.Column(db.Integer)
    azul = db.Column(db.Integer) 


    def __init__(self, idUsuario, idProducto,longitud, anchura, rojo, verde, azul):
        self.idUsuario = idUsuario
        self.idProducto = idProducto
        self.fecha = fecha
        self.longitud = longitud
        self.anchura = anchura
        self.rojo = rojo
        self.verde = verde
        self.azul = azul


    def __repr__(self):
        return ''