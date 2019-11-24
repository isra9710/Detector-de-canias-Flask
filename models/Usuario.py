from sqlalchemy.orm import relationship
from models.Shared import db


class Usuario(db.Model):
    __tablename__ = 'Usuario'
    idUsuario = db.Column(db.Integer, primary_key=True)
    nombreUsuario = db.Column(db.String(15), unique=True)
    contra = db.Column(db.String(10))
    tipo = db.Column(db.String(15))
    resultado = relationship ("Resultado", backref= "Usuario")

    def __init__(self, nombreUsuario, contra, tipo):

        self.nombreUsuario = nombreUsuario
        self.contra = contra
        self.tipo = tipo

    def __repr__(self):
        return ''
