from flask import Flask, render_template, request, session, flash, redirect, url_for
import os
import cv2
import uuid
import matplotlib.pyplot as plt

app = Flask(__name__)
SECRET_KEY = "my_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cania'  # conexion con la base de datos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Cosa extra para evitar notificaciones
from config import *  # en el archivo config se encuentran importadas todas las clases, esto para tener menos codigo en el main
from models.Shared import db  # se importa el objeto de SQLAlchemy para tenerlo en todos los modulos que se necesiten


@app.route("/")
def index():
   return render_template("login.html")




@app.route("/crud")
def crud():
    return render_template("crud.html")


@app.route("/login")
def login():
   return render_template("login.html")




@app.route("/abrir")
def abrir():
    print(cv2.__version__)
    imagen = cv2.imread("cania.jpg",1)
    plt.imshow(imagen, cmap = 'gray', interpolation = 'bicubic')
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()


@app.route("/tomar")
def tomar():

    cap = cv2.VideoCapture(0)
    nombre_foto = ""
    leido, frame = cap.read()
    if leido:
        nombre_foto = str(
            uuid.uuid4()) + ".png"  # uuid4 regresa un objeto, no una cadena. Por eso lo convertimos
        guardar = "static/" + nombre_foto
        cv2.imwrite(guardar, frame)

        color = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        nombre_foto = str(
            uuid.uuid4()) + ".png"
        guardar = "static/" + nombre_foto
        cv2.imwrite(guardar, color)
        cap.release()
        producto = Producto(nombre_foto)
        db.session.add(producto)
        db.session.commit()
        print("Foto tomada correctamente con el nombre {}".format(nombre_foto))
    else:
        print("Error al acceder a la cámara")

    """
    	Finalmente liberamos o soltamos la cámara
    """
    return render_template("captura.html", nombre_foto=nombre_foto)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)