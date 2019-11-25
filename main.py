from flask import Flask, render_template, request, session, flash, redirect, url_for
import os
from os import remove
import cv2
import uuid
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
from matplotlib import pyplot as plt

app = Flask(__name__)
SECRET_KEY = "my_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cania'  # conexion con la base de datos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Cosa extra para evitar notificaciones
from config import *  # en el archivo config se encuentran importadas todas las clases, esto para tener menos codigo en el main
from models.Shared import db  # se importa el objeto de SQLAlchemy para tenerlo en todos los modulos que se necesiten


@app.route("/")
def index():
   return render_template("login.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    usuario = Usuario.query.filter_by(nombreUsuario=request.form['usuario']).first()
    if usuario:
        if usuario.contra == request.form.get("contra"):
            if usuario.tipo == "Administrador":
                session['username'] = request.form['usuario']
                return redirect((url_for('homeAdmin')))
            elif usuario.tipo == "Empleado":
                session['username'] = request.form['usuario']
                return redirect((url_for('homeEmpleado')))
        else:
            flash("Usuario o contraseña incorrecta")
            return redirect((url_for('index')))
    else:
        flash("Usuario o contraseña incorrecta")
        return redirect((url_for('index')))


@app.route("/homeAdmin")
def homeAdmin():
    return render_template("administrador/home.html")


@app.route("/crudUsuario", methods=['GET', 'POST'])
def crudUsuario():
    usuarios = Usuario.query.all()
    return render_template("administrador/crudUsuario.html", usuarios = usuarios)


@app.route("/agregarUsuario", methods=['GET', 'POST'])
def agregarUsuario():
    if  request.method == 'POST': 
        usuario = Usuario.query.filter_by(nombreUsuario=request.form["nombre"]).first()
        if usuario:
            flash("Ese nombre de usuario ya existe ya existe")
            return redirect((url_for('crudUsuario')))
        else:
            usuario = Usuario(request.form.get("nombre"), request.form.get("contra"),"Empleado")
            flash("Se agregó usuario con éxito")
            db.session.add(usuario)
            db.session.commit()
            return redirect((url_for('crudUsuario')))
    else:      
        flash("No se agregó usuario con éxito")  
        return redirect((url_for('crudUsuario')))
        

@app.route("/llenarEditarUsuario/<string:id>", methods=['Get', 'POST'])
def llenarEditarUsuario(id):
    usuario = Usuario.query.filter_by(idUsuario=id).first()
    return render_template("administrador/editarUsuario.html", usuario = usuario)


@app.route("/editarUsuario", methods=['GET', 'POST'])
def editarUsuario():
    usuarioO = Usuario.query.filter_by(idUsuario=request.form['id']).first()
    if validarNombreU(usuarioO.nombreUsuario, request.form['nombre']):
        usuarioO.nombreUsuario = request.form['nombre']
        usuarioO.tipo = request.form['tipo']
        flash("Usuario editado con éxtio")
        db.session.commit()
        return redirect((url_for('crudUsuario')))
    else:
        flash("Ocurrió un problema al editar, quizá ingreso un dato repetido o erroneo")
        return redirect((url_for('crudUsuario')))


def validarNombreU(nombreO, nombreN):
    usuarioO = Usuario.query.filter_by(nombreUsuario=nombreO).first()
    if nombreO == nombreN:
        return True
    else:
        usuarioN = Usuario.query.filter(Usuario.idUsuario != usuarioO.idUsuario, Usuario.nombreUsuario == nombreN).all()
        if usuarioN:
            return False
        else:
            return True


@app.route("/eliminarUsuario/<string:id>", methods=['Get', 'POST'])
def eliminarUsuario(id):
    usuario = Usuario.query.filter_by(idUsuario=id).first()
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado con éxito")
    return redirect((url_for('crudUsuario')))

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)
    
def agregarImagen(f):
    folder = os.path.realpath(__file__).replace('\\', '/').split('/')[0:-1]
    f.save('/'.join(folder) + '/static/' + f.filename)
    nombre = str(f.filename)
    return nombre

@app.route("/crudCania", methods=['GET','POST'])
def crudCania():
    resultados = Resultado.query.all()
    return render_template("administrador/crudCania.html", resultados=resultados)


@app.route("/experimento", methods=['GET','POST'])
def experimento():
    if request.method == "POST":
        f = request.files['file']
        nombre = agregarImagen(f)
        image = cv2.imread("static/" + nombre)#Se lee la imagen
        image = imutils.resize(image,width=300, height=500)#Se redimensiona
        img = cv2.imread("static/" + nombre,1)
        img = imutils.resize(img,width=300, height=500)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#
        gris = gray
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        edged = cv2.Canny(gray, 50, 100)
        bordes = edged
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        (cnts, _) = contours.sort_contours(cnts)
        pixelsPerMetric = None
        i = 0
        array = ""
        dimA = ""
        dimB = ""
        for c in cnts:
            
            if cv2.contourArea(c) < 100:
                continue
            i= i+1
            orig = image.copy()
            box = cv2.minAreaRect(c)
            box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
            box = np.array(box, dtype="int")
            box = perspective.order_points(box)
            cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
            for (x, y) in box:
                cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1) 
            (tl, tr, br, bl) = box
            (tltrX, tltrY) = midpoint(tl, tr)
            (blbrX, blbrY) = midpoint(bl, br)
            (tlblX, tlblY) = midpoint(tl, bl)
            (trbrX, trbrY) = midpoint(tr, br)
            cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
            cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
            cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
            cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)
            cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
                (255, 0, 255), 2)
            cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
                (255, 0, 255), 2)
            dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
            dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY)) 
            if pixelsPerMetric is None:
                pixelsPerMetric = dB / 4.2
            dimA = dA / pixelsPerMetric
            dimB = dB / pixelsPerMetric   
            cv2.putText(orig, str (dimA) + "cm",
                (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (255, 255, 255), 2)
            cv2.putText(orig, str (dimB) + "cm",
                (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (255, 255, 255), 2)
            if i == 2:
                if cv2.contourArea(c) >800: # filter small contours
                    x,y,w,h = cv2.boundingRect(c) # offsets - with this you get 'mask'
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    print('Color promdio de la figura (Azul, Verde, Rojo): ',np.array(cv2.mean(img[y:y+h,x:x+w])).astype(np.uint8))
                    array = np.array(cv2.mean(img[y:y+h,x:x+w])).astype(np.uint8)
        nombreM = str(
            uuid.uuid4()) + ".png"  # uuid4 regresa un objeto, no una cadena. Por eso lo convertimos
        guardar = "static/" + nombreM
        cv2.imwrite(guardar, orig)
        nombreC = str(
            uuid.uuid4()) + ".png"  # uuid4 regresa un objeto, no una cadena. Por eso lo convertimos
        guardar = "static/" + nombreC
        cv2.imwrite(guardar, img)
        flash("Antes de guardar el experimento asegurate de que la imagen fue procesada de manera adecuada")
        return render_template("administrador/ver.html", nombre = nombre, medida = nombreM, color = nombreC, colores = array, anchura = dimB, altura = dimA)


@app.route("/agregarExp", methods=['GET','POST'])
def agregarExp():
    if  request.method == 'POST':
        nombre = session['username']




@app.route("/agregaRep", methods=['GET','POST'])
def agregaRep():
    return "hola"


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)