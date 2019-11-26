from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from models.Shared import db
import datetime
from datetime import date, time

class Resultado(db.Model):
    __tablename__ = 'Resultado'
    idResultado = db.Column(db.Integer, primary_key=True)
    idUsuario = db.Column('idUsuario', db.Integer, db.ForeignKey("Usuario.idUsuario"))
    idP = db.Column('idP', db.Integer, db.ForeignKey("Producto.idP"))
    fecha = db.Column(db.Date,default=date.today)
    hora = db.Column(db.DateTime, default=datetime.datetime.now())
    longitud = db.Column(db.Float)
    anchura = db.Column(db.Float)
    rojo = db.Column(db.Integer)
    verde = db.Column(db.Integer)
    azul = db.Column(db.Integer)
    imgM = db.Column(db.String(300))
    imgC = db.Column(db.String(300)) 
    img = relationship("Producto", back_populates="resultado")


    def __init__(self, idUsuario, idP,longitud, anchura, rojo, verde, azul, imgM, imgC):
        self.idUsuario = idUsuario
        self.idP = idP
        self.longitud = longitud
        self.anchura = anchura
        self.rojo = rojo
        self.verde = verde
        self.azul = azul
        self.imgM = imgM
        self.imgC = imgC

    def __repr__(self):
        return ''