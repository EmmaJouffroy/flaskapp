from flask import Flask, request, render_template, make_response, send_file, url_for, session, redirect, g
import pymysql
import io
from io import StringIO, BytesIO
import mysql.connector
import os
import bcrypt
from pdf2image import convert_from_path, convert_from_bytes
import tempfile
from PIL import Image
import base64
import collections
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import pandas as pd
import numpy as np
from numpy import array, argmax
import pickle
import pdfkit
from keras import backend as K
from flask_login import current_user
from forms import SearchForm


connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             db='flaskapp',
                             port=8889,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__)


def write_file(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)


def ValuePredictor(to_predict_list):
    loaded_model = pickle.load(open("model.pkl", "rb"))
    result = loaded_model.predict(to_predict_list)
    return result[0]


def ShowImg(allPdfBlob, i):
    fileData = allPdfBlob[i]['contentPdf']
    write_file(fileData, 'cv{{i}}.pdf')
    with open('cv{{i}}.pdf', 'rb') as file:
        fileData = file.read()

    filename = 'cv{{i}}.pdf'
    with tempfile.TemporaryDirectory() as path:
        images_from_path = convert_from_path(
            filename, output_folder=path, last_page=1, first_page=0)

        base_filename = os.path.splitext(
            os.path.basename(filename))[0] + '.jpeg'
        save_dir = io.BytesIO()

    for page in images_from_path:
        page.save(save_dir, 'jpeg', filename=base_filename)
        save_dir.seek(0)
        page = base64.b64encode(save_dir.getvalue())
        page = page.decode('ascii')
    return page


def Enquiry(lis1):
    if len(lis1) == 0:
        return 0
    else:
        return 1


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("home.html")


@app.route('/cvgenerator', methods=["GET", "POST"])
def generateCV():
    return render_template("cvgenerator.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    else:
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        status = request.form['status']
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        with connection.cursor() as cursor:
            sqlUsers = "INSERT INTO users (email, password, status) VALUES (%s,%s,%s)"
            cursor.execute(sqlUsers,  (email, hash_password, status))
            connection.commit()
            session['email'] = request.form['email']
            email = session['email']
            session['status'] = request.form['status']
            cursor.close()

        with connection.cursor() as cursor:
            sqlUsers = "SELECT `IDusers` FROM `users` WHERE `email`=%s"
            cursor.execute(sqlUsers, email)
            idUser = cursor.fetchone()
            cursor.close()

            session['idUser'] = idUser['IDusers']

            return redirect(url_for('home'))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        with connection.cursor() as cursor:
            sqlUsers = "SELECT `IDusers`, `password` FROM `users` WHERE `email`=%s"
            cursor.execute(sqlUsers, email)
            users = cursor.fetchall()
            cursor.close()

        if len(users) > 0:
            if bcrypt.checkpw(password, hashed):
                with connection.cursor() as cursor:
                    sqlCheckUser = "SELECT * FROM `users` WHERE `email`=%s"
                    cursor.execute(sqlCheckUser, email)
                    user = cursor.fetchone()
                    session['email'] = user['email']
                    session['status'] = str(user['status'])
                    session['idUser'] = user['IDusers']
                    cursor.close()
                    return render_template("home.html")
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("login.html")


@app.route("/forward/", methods=['POST'])
def move_forward():

    # On récupère toutes les données envoyées
    datas = request.form
    firstname = datas['firstname']
    lastname = datas['lastname']
    img = datas['img']
    resume = datas['resume']
    title = datas['title']
    choicesskills = request.values.getlist('skills[]')
    skill1 = choicesskills[0]
    skill2 = choicesskills[1]
    skill3 = choicesskills[2]
    skill4 = choicesskills[3]
    choiceshobbies = request.values.getlist('hobbies[]')
    hobby1 = choiceshobbies[0]
    hobby2 = choiceshobbies[1]
    hobby3 = choiceshobbies[2]
    emailUser = session['email']

    rendered = render_template('pdf_template.html', donneesForm=datas)
    css = ['main.css']
    pdf = pdfkit.from_string(rendered, 'test.pdf', css=css)

    with open('test.pdf', 'rb') as file:
        binaryData = file.read()

    filename = 'test.pdf'

    with connection.cursor() as cursor:
        sqlIdUser = 'SELECT `IDusers` FROM `users` WHERE `email`=%s'
        cursor.execute(sqlIdUser, emailUser)
        idUser = cursor.fetchone()
        SessionID = str(idUser['IDusers'])
        session['idUser'] = SessionID

        sqlCv = 'INSERT INTO cv(IDusers, firstname, lastname, img, resume, title) VALUES (%s,%s,%s,%s,%s,%s)'
        cursor.execute(sqlCv, (SessionID, firstname,
                               lastname, img, resume, title))
        connection.commit()

        sqlLastId = 'SELECT `IDcv` FROM cv INNER JOIN users ON cv.IDusers=users.IDusers WHERE IDcv = LAST_INSERT_ID()  '
        cursor.execute(sqlLastId)
        lastIdCVUser = cursor.fetchone()
        lastIdCV = str(lastIdCVUser['IDcv'])

        sqlHobbies = 'INSERT INTO hobbies (IDcv, hobby1, hobby2, hobby3) VALUES (%s,%s,%s,%s)'
        cursor.execute(sqlHobbies, (lastIdCV, hobby1, hobby2, hobby3))
        connection.commit()

        sqlSkills = 'INSERT INTO skills (IDcv,skill1,skill2,skill3,skill4) VALUES (%s,%s,%s,%s,%s)'
        cursor.execute(sqlSkills, (lastIdCV, skill1, skill2, skill3, skill4))
        connection.commit()

        sqlGenerated = 'INSERT INTO pdfGenerated (contentPdf,idUser, idCv) VALUES (%s,%s,%s)'
        cursor.execute(sqlGenerated, (binaryData, SessionID, lastIdCV))
        connection.commit()
        cursor.close()

    x = []

    x.append(skill1)
    x.append(skill2)
    x.append(skill3)
    x.append(skill4)
    x.append(hobby1)
    x.append(hobby2)
    x.append(hobby3)

    x = array([[x[0], x[1], x[2], x[3], x[4], x[5], x[6]]])
    query_df = pd.DataFrame(x)
    query = pd.get_dummies(query_df, prefix=[
                           'compétence1', 'compétence2', 'compétence3', 'compétence4', 'hobby1', 'hobby2', 'hobby3'])
    model_columns = pickle.load(open("model_columns.pkl", "rb"))

    for col in model_columns:
        if col not in query.columns:
            query[col] = 0

    K.clear_session()
    result = ValuePredictor(query)

    pred1 = float(result[0])
    pred2 = float(result[1])
    pred3 = float(result[2])
    pred4 = float(result[3])

    with connection.cursor() as cursor:
        sqlPredictions = 'INSERT INTO predictions (pers1,pers2,pers3,pers4,idCv) VALUES (%s,%s,%s,%s,%s)'
        cursor.execute(sqlPredictions, (pred1, pred2, pred3, pred4, lastIdCV))
        connection.commit()
        cursor.close()

    os.remove("test.pdf")
    return render_template("home.html")


@app.route('/myAction/', methods=["GET", "POST"])
def candidatePrediction():
    idPdf = request.args.get('idPdf')

    with connection.cursor() as cursor:
        sqlContentPdf = "SELECT contentPdf FROM `pdfGenerated` WHERE `id`=%s"
        cursor.execute(sqlContentPdf, idPdf)
        allPdfBlob = cursor.fetchone()
        cursor.close()

    fileData = allPdfBlob['contentPdf']
    write_file(fileData, 'cv.pdf')

    with open('cv.pdf', 'rb') as file:
        fileData = file.read()

    filename = 'cv.pdf'

    with tempfile.TemporaryDirectory() as path:
        images_from_path = convert_from_path(
            filename, output_folder=path, last_page=1, first_page=0)

    base_filename = os.path.splitext(os.path.basename(filename))[0] + '.jpeg'
    save_dir = io.BytesIO()

    for page in images_from_path:
        page.save(save_dir, 'jpeg', filename=base_filename)
        save_dir.seek(0)
        page = base64.b64encode(save_dir.getvalue())

    with connection.cursor() as cursor:
        sqlIdCv = "SELECT `idCv` FROM `pdfGenerated` WHERE `id`=%s"
        cursor.execute(sqlIdCv, idPdf)
        idCv = cursor.fetchone()
        cursor.close()
    idCv = idCv['idCv']

    with connection.cursor() as cursor:
        sqlPredictions = "SELECT `*` FROM `predictions` WHERE `idCv`=%s"
        cursor.execute(sqlPredictions, idCv)
        results = cursor.fetchall()
        cursor.close()

    os.remove("cv.pdf")

    return render_template("candidatePrediction.html", page=page.decode('ascii'), predictions=results)


@app.route('/candidatesAllCv', methods=["GET", "POST"])
def candidatesAllCv():

    with connection.cursor() as cursor:
        sqlContentPdf = "SELECT contentPdf FROM `pdfGenerated` WHERE `IdUser`=%s"
        cursor.execute(sqlContentPdf, session['idUser'])
        allPdfBlob = cursor.fetchall()
        cursor.close()

        if Enquiry(allPdfBlob):
            tabImg = []
            fileData = []
            i = 0

            while i < len(allPdfBlob):
                page = ShowImg(allPdfBlob, i)
                tabImg.append(page)
                i += 1
            os.remove("cv{{i}}.pdf")
            return render_template('candidatesAllCv.html', len=len(tabImg), images=tabImg)
        else:
            return render_template('home.html')


@app.route('/recruitersAllCv', methods=["GET", "POST"])
def recruitersAllCv():

    if not session.get('idCvDomain'):
        with connection.cursor() as cursor:
            sql = "SELECT id, contentPdf FROM `pdfGenerated`"
            cursor.execute(sql)
            allPdfBlob = cursor.fetchall()
            cursor.close()

        if Enquiry(allPdfBlob):
            fileData = []
            i = 0
            tabImg = []
            idPdf = []

            while i < len(allPdfBlob):
                idUnique = allPdfBlob[i]['id']
                page = ShowImg(allPdfBlob, i)
                tabImg.append(page)
                idPdf.append(idUnique)
                i += 1
                os.remove("cv{{i}}.pdf")
            return render_template('recruitersAllCv.html', len=len(tabImg), images=tabImg, idPdf=idPdf)
        else:
            return render_template('home.html')
    else:

        idCvs = session['idCvDomain']
        i = 0
        allPdfBlob = []
        fileData = []
        tabImg = []
        idPdf = []

        while i < len(idCvs):
            idCv = idCvs[i]
            idCv = idCv['IDcv']

            with connection.cursor() as cursor:
                sqlContentPdf = "SELECT id, contentPdf FROM `pdfGenerated` WHERE `idCv`=%s"
                cursor.execute(sqlContentPdf, idCv)
                Blob = cursor.fetchone()
                allPdfBlob.append(Blob)
                cursor.close()
                i += 1
        j = 0
        while j < len(allPdfBlob):
            idUnique = allPdfBlob[j]['id']
            page = ShowImg(allPdfBlob, j)
            tabImg.append(page)
            idPdf.append(idUnique)
            j += 1
            os.remove("cv{{i}}.pdf")
        return render_template('recruitersAllCv.html', len=len(tabImg), images=tabImg, idPdf=idPdf)


@app.route('/search', methods=['POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('home'))
    else:
        search = g.search_form.search.data
        print(search)
        with connection.cursor() as cursor:
            sql = "SELECT IDcv FROM `cv` where `domain`=%s  "
            cursor.execute(sql, search)
            idcv = cursor.fetchall()
            session['idCvDomain'] = idcv
            cursor.close()
    return redirect(url_for('recruitersAllCv'))


@app.before_request
def before_request():
    g.user = current_user
    g.search_form = SearchForm()


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
