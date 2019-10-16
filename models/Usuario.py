from sqlalchemy.orm import relationship
from models.Shared import db


class Cliente(db.Model):
    __tablename__ = 'Cliente'
    idCliente = db.Column(db.Integer, primary_key=True)
    idUsuario = db.Column(db.Integer, db.ForeignKey("Usuario.idUsuario"))
    rfc = db.Column(db.String(13))
    direccion = db.Column(db.String(30))
    nombreEstablecimiento = db.Column(db.String(30))
    pedido = relationship("Pedido", backref="Usuario")

    def __init__(self, idUsuario, rfc, direccion, nombre, apellidoP):
        self.idUsuario = idUsuario
        self.rfc = rfc
        self.direccion = direccion
        self.nombreEstablecimiento = nombre

    def __repr__(self):
        return ''
