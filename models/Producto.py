from sqlalchemy.orm import relationship
from models.Shared import db


class Producto(db.Model):
    __tablename__ = 'Producto'
    idP = db.Column(db.Integer, primary_key=True)
    #idUsuario = db.Column(db.Integer, db.ForeignKey("Usuario.idUsuario"))
    #rfc = db.Column(db.String(13))
    #direccion = db.Column(db.String(30))
    #nombreEstablecimiento = db.Column(db.String(30))
    #pedido = relationship("Pedido", backref="Usuario")
    img = db.Column(db.String(300))

    def __init__(self, img):
        self.img = img

    def __repr__(self):
        return ''