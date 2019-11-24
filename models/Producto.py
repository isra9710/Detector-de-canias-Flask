from sqlalchemy.orm import relationship
from models.Shared import db


class Producto(db.Model):
    __tablename__ = 'Producto'
    idP = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(300))
    resultado = relationship ("Resultado", backref= "Producto")

    def __init__(self, img):
        self.img = img

    def __repr__(self):
        return ''