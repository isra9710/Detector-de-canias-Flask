from flask import Flask, render_template, request, session, flash, redirect, url_for
import os
from os import remove
import datetime
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
import flask_weasyprint
from flask_weasyprint import HTML, render_pdf
from sqlalchemy import or_
app = Flask(__name__)
SECRET_KEY = "my_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cania'  # conexion con la base de datos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Cosa extra para evitar notificaciones
from config import *  # en el archivo config se encuentran importadas todas las clases, esto para tener menos codigo en el main
from models.Shared import db  # se importa el objeto de SQLAlchemy para tenerlo en todos los modulos que se necesiten


@app.route("/")#Este decorador nos lleva a la página principal que es el login
def index():
   return render_template("login.html")


@app.route("/login", methods=['GET', 'POST'])#Este decorador llama a la función para validar los datos de inicio de sesión
def login():
    usuario = Usuario.query.filter_by(nombreUsuario=request.form['usuario']).first()
    if usuario:
        if usuario.contra == request.form.get("contra"):
            session['username'] = request.form['usuario']#Con el uso de sesiones se guardan datos
            session['id'] = usuario.idUsuario#en estas tres líneas se guarda el nombre de usuario, el id del mismo
            session['tipo'] = usuario.tipo# y por último el tipo de usuario
            if usuario.tipo == "Administrador":
                return redirect((url_for('homeAdmin')))
            elif usuario.tipo == "Empleado":
                return redirect((url_for('homeEmpleado')))
        else:
            flash("Usuario o contraseña incorrecta")#Con la palabra reservada flash se mandan mensajes hacia el html
            return redirect((url_for('index')))
    else:
        flash("Usuario o contraseña incorrecta")
        return redirect((url_for('index')))


@app.route("/logout")#Decorador para cerrar sesión
def logout():
    session.pop('username')#Destruye todos los datos
    session.pop('id')#Generados durante
    session.pop('tipo')#La sesión
    return redirect((url_for('index')))


@app.route("/homeAdmin")
def homeAdmin():
    return render_template("administrador/home.html")

@app.route("/homeUs")
def homeUs():
    return render_template("usuario/home.html")


@app.route("/crudUsuario", methods=['GET', 'POST'])#Este decorador nos muestra la página principal para el crud de usuarios
def crudUsuario():
    usuarios = Usuario.query.all()#Se hace una consulta a la base de datos, regresando una lista
    return render_template("administrador/crudUsuario.html", usuarios = usuarios)#por éso el nombre en plural


@app.route("/agregarUsuario", methods=['GET', 'POST'])
def agregarUsuario():
    if  request.method == 'POST': 
        usuario = Usuario.query.filter_by(nombreUsuario=request.form["nombre"]).first()#Se valida que el usuario a registrar no esté en la base de datos mediante una consulta
        if usuario:#Si el usuario existe, se regresa a la página con un mensaje de no registrado
            flash("Ese nombre de usuario ya existe ya existe")
            return redirect((url_for('crudUsuario')))
        else:
            usuario = Usuario(request.form.get("nombre"), request.form.get("contra"),"Empleado")#Si no con los datos del html se crea un nuevo objeto haciendo uso de su constructor
            flash("Se agregó usuario con éxito")
            db.session.add(usuario)#Se hace uso del objeto y con el ORM se añade el objeto con los datos a la base
            db.session.commit()#Se afirma la actualización de datos
            return redirect((url_for('crudUsuario')))
    else:      
        flash("No se agregó usuario con éxito")  
        return redirect((url_for('crudUsuario')))
        

@app.route("/llenarEditarUsuario/<string:id>", methods=['Get', 'POST'])#Este decorador recibe un id del form
def llenarEditarUsuario(id):#Lo maneja en la función
    usuario = Usuario.query.filter_by(idUsuario=id).first()#Se hace una consulta para poder mostrar los datos del objeto en otro html
    return render_template("administrador/editarUsuario.html", usuario = usuario)


@app.route("/editarUsuario", methods=['GET', 'POST'])#Esta función se encarga de llamar a la función para editar
def editarUsuario():
    usuarioO = Usuario.query.filter_by(idUsuario=request.form['id']).first()#se crea un objeto "Original"
    if validarNombreU(usuarioO.nombreUsuario, request.form['nombre']):#Se valida el nombre del usuario para que no se repitan
        usuarioO.nombreUsuario = request.form['nombre']
        usuarioO.tipo = request.form['tipo']
        flash("Usuario editado con éxtio")
        db.session.commit()
        return redirect((url_for('crudUsuario')))
    else:
        flash("Ocurrió un problema al editar, quizá ingreso un dato repetido o erroneo")
        return redirect((url_for('crudUsuario')))


def validarNombreU(nombreO, nombreN):#Esta función sirve para validar nombres, recibiendo el nombre original y el nuevo nombre como parametro
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
    tipo = session['tipo']
    resultados = Resultado.query.all()
    if tipo == "Administrador":
        return render_template("administrador/crudCania.html", resultados=resultados)
    else: 
        return render_template("usuario/crudCania.html", resultados=resultados)


@app.route("/experimento", methods=['GET','POST'])
def experimento():
    if request.method == "POST":
        f = request.files['file']
        nombre = agregarImagen(f)
        image = cv2.imread("static/" + nombre)#Se lee la imagen para las medidas
        image = imutils.resize(image,width=300, height=500)#Se redimensiona
        img = cv2.imread("static/" + nombre,1)#Se lee la imagen para el color
        img = imutils.resize(img,width=300, height=500)#Se redimensiona
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#Se aplica cambio de BGR a Grises
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        edged = cv2.Canny(gray, 50, 100)
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
            if i == 2:#Sólo nos sirve el segundo borde encontrado, es decir la segunda figura encontrada
                if cv2.contourArea(c) >800: 
                    x,y,w,h = cv2.boundingRect(c) # Con ésto se obtiene la máscara
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
        tipo = session['tipo']
        if tipo == "Administrador":
            flash("Antes de guardar el experimento asegurate de que la imagen fue procesada de manera adecuada")
            return render_template("administrador/ver.html", nombre = nombre, medida = nombreM, color = nombreC, colores = array, anchura = dimB, altura = dimA)
        else:
            flash("Antes de guardar el experimento asegurate de que la imagen fue procesada de manera adecuada")
            return render_template("usuario/ver.html", nombre = nombre, medida = nombreM, color = nombreC, colores = array, anchura = dimB, altura = dimA)


@app.route("/agregarExp", methods=['GET','POST'])
def agregarExp():
    if  request.method == 'POST':
        nombre = session['username']
        producto = Producto(request.form.get("foto"))
        db.session.add(producto)
        db.session.commit()
        producto = Producto.query.filter_by(img = request.form.get("foto")).first()
        idUsuario = session['id']
        print(producto.idP)
        resultado = Resultado(idUsuario, producto.idP,float(request.form.get("altura")), float(request.form.get("anchura")), int(request.form.get("rojo")), int(request.form.get("verde")), int(request.form.get("azul")), request.form.get("medida"), request.form.get("color") )
        db.session.add(resultado)
        db.session.commit()
        flash("La Experimentación se hizo con éxito")
        return redirect((url_for('crudCania')))


@app.route("/llenarEditarExp/<string:id>", methods=['Get', 'POST'])
def llenarEditarExp(id):
    resultado = Resultado.query.filter_by(idResultado = id).first()
    tipo = session['tipo']
    if tipo == "Administrador":
        return render_template("administrador/editarExp.html", resultado = resultado)
    else:
        return render_template("usuario/editarExp.html", resultado = resultado)


@app.route("/editarExp", methods=['GET', 'POST'])#Esta función se encarga de llamar a la función para editar
def editarExp():
        idR = request.form.get("id")
        resultado = Resultado.query.filter_by(idResultado = idR).first()
        altura = request.form.get("altura")
        anchura = request.form.get("anchura")
        rojo = request.form.get("rojo")
        verde = request.form.get("verde")
        azul = request.form.get("azul")
        resultado.longitud = altura
        resultado.anchura = anchura
        resultado.rojo = rojo
        resultado.verde = verde
        resultado.azul = azul
        flash("Experimento editado con éxtio")
        db.session.commit()
        return redirect((url_for('crudCania')))
    

@app.route("/eliminarExp/<string:id>", methods=['GET', 'POST'])
def eliminarExp(id):
    resultado = Resultado.query.filter_by(idResultado=id).first()
    imagen = Producto.query.filter_by(idP = resultado.idP).first()
    db.session.delete(resultado)
    db.session.delete(imagen)
    ruta = "static/"
    img = ruta + imagen.img
    med = ruta + resultado.imgM
    col = ruta + resultado.imgC
    remove(img)
    remove(med)
    remove(col)
    db.session.commit()
    flash("Experimento eliminado con éxito")
    return redirect((url_for('crudCania')))
          

@app.route("/agregaRep", methods=['GET','POST'])
def agregaRep():
    tipo = session['tipo']
    if tipo == "Administrador":
        return render_template("administrador/fechaR.html")
    else:
        return render_template("usuario/fechaR.html")


@app.route("/generarReporte", methods=['GET', 'POST'])
def generarReporte():
    tipo = session['tipo']
    resultados = ""
    fecha = ""
    if request.form.get("fechaDia") is not None:
        fecha = request.form.get("fechaDia")
        session ['fecha'] = fecha
        resultados = Resultado.query.filter_by(fecha = fecha).all()
    else:
        fecha = request.form.get("fechaS")
        session['fecha'] = fecha
        fecha2 = fecha + datetime.timedelta(days=7)
        session['fecha2'] = fecha2
    if tipo == "Administrador":
        return render_template("administrador/reporte.html", resultados = resultados, fecha = fecha, fecha2 = None)
    else: 
        return render_template("usuario/reporte.html", resultados = resultados, fecha = fecha, fecha2 = fecha2)


@app.route("/generarPDF", methods=['GET', 'POST'])
def generarPDF():
    fecha = session['fecha']
    fecha2 = session['fecha2']
    resultados = ""
    if fecha2 is None:
        resultados = Resultado.query.filter_by(fecha = fecha).all()
        html = render_template("pdf.html", resultados = resultados, fecha = fecha, fecha2 = None)
    else:
        resultados = filter(or_(Resultado.fecha == fecha, Resultado.fecha == fecha2))
        html = render_template("pdf.html", resultados = resultados, fecha = fecha, fecha2 = None)
    return render_pdf(HTML(string=html))


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)