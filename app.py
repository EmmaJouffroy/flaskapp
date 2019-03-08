from flask import Flask, request, render_template, make_response, send_file, url_for, session, redirect
import pymysql
from io import StringIO, BytesIO
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import mysql.connector
import os
import bcrypt
from pdf2image import convert_from_path, convert_from_bytes
import tempfile
import io
from PIL import Image
import base64


connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             db='flaskapp',
                             port=8889,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html")


@app.route("/forward/", methods=['POST'])
def move_forward():
    # img = request.form['img']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    title = request.form['title']
    resume = request.form['resume']
    form1Title = request.form['form1Title']
    form1Text = request.form['form1Text']
    form2Title = request.form['form2Title']
    form2Text = request.form['form2Text']
    form3Title = request.form['form3Title']
    form3Text = request.form['form3Text']
    exp1Title = request.form['exp1Title']
    exp1Resume = request.form['exp1Resume']
    exp2Title = request.form['exp2Title']
    exp2Resume = request.form['exp2Resume']
    exp3Title = request.form['exp3Title']
    exp3Resume = request.form['exp3Resume']
    language1 = request.form['language1']
    language2 = request.form['language2']
    language3 = request.form['language3']
    choicesskills = request.values.getlist('skills[]')
    skill1 = choicesskills[0]
    skill2 = choicesskills[1]
    skill3 = choicesskills[2]
    skill4 = choicesskills[3]
    skill5 = choicesskills[4]
    choiceshobbies = request.values.getlist('hobbies[]')
    hobby1 = choiceshobbies[0]
    hobby2 = choiceshobbies[1]
    hobby3 = choiceshobbies[2]
    phoneNumber = request.form['phoneNumber']
    email = request.form['email']
    websiteTitle = request.form['websiteTitle']
    websiteLink = request.form['websiteLink']
    sm1Title = request.form['sm1Title']
    sm1Link = request.form['sm1Link']
    sm2Title = request.form['sm2Title']
    sm2Link = request.form['sm2Link']
    exp1Debut = request.form['exp1Debut']
    exp1Fin = request.form['exp1Fin']
    exp2Debut = request.form['exp2Debut']
    exp2Fin = request.form['exp2Fin']
    exp3Debut = request.form['exp3Debut']
    exp3Fin = request.form['exp3Fin']
    form1Debut = request.form['form1Debut']
    form1Fin = request.form['form1Fin']
    form2Debut = request.form['form2Debut']
    form2Fin = request.form['form2Fin']
    form3Debut = request.form['form3Debut']
    form3Fin = request.form['form3Fin']
    emailUser = session['email']

    output = StringIO()
    doc = SimpleDocTemplate("test.pdf", pagesize=letter)
    Story = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    ptext = """<font size=12>%s</font>""" % (title)
    p1text = """<font size=15>%s</font>""" % (resume)
    p2text = """<font size=10>%s</font>""" % (email)
    p3text = """<font size=9>%s</font>""" % (sm2Title)
    p4text = """<font size=6>%s</font>""" % (sm2Link)

    Story.append(Paragraph(ptext, styles["Justify"]))
    Story.append(Paragraph(p1text, styles["Justify"]))
    Story.append(Paragraph(p2text, styles["Justify"]))
    Story.append(Paragraph(p3text, styles["Justify"]))
    Story.append(Paragraph(p4text, styles["Justify"]))

    doc.build(Story)
    pdf_out = output.getvalue()
    output.close()

    response = make_response(pdf_out)
    response.headers['Content-Disposition'] = "attachment; filename='test.pdf"
    response.mimetype = 'application/pdf'

    with open('test.pdf', 'rb') as file:
        binaryData = file.read()

    filename = 'test.pdf'
    with tempfile.TemporaryDirectory() as path:
        images_from_path = convert_from_path(
            filename, output_folder=path, last_page=1, first_page=0)

    base_filename = os.path.splitext(os.path.basename(filename))[0] + '.jpg'
    save_dir = 'templates'

    for page in images_from_path:
        img = page.save(os.path.join(save_dir, base_filename), 'JPEG')

    with connection.cursor() as cursor:
        sql = 'SELECT `IDusers` FROM `users` WHERE `email`=%s'
        cursor.execute(sql, emailUser)
        idUser = cursor.fetchone()
        SessionID = str(idUser['IDusers'])
        session['idUser'] = SessionID
        cursor.close()

    with connection.cursor() as cursor:
        sql = 'INSERT INTO cv(IDusers, firstname, lastname, img, resume, title, contentPdf) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(sql, (SessionID, firstname,
                             lastname, img, resume, title, binaryData))
        connection.commit()
        cursor.close()

    with connection.cursor() as cursor:
        sql = 'SELECT `IDcv` FROM cv INNER JOIN users ON cv.IDusers=users.IDusers WHERE IDcv = LAST_INSERT_ID()  '
        cursor.execute(sql)
        lastIdCVUser = cursor.fetchone()
        lastIdCV = str(lastIdCVUser['IDcv'])
        cursor.close()

    with connection.cursor() as cursor:
        sql = 'INSERT INTO experience (IDcv, exp1Title, exp1Resume, exp2Title, exp2Resume, exp3Title, exp3Resume,exp1Debut,exp1Fin,exp2Debut,exp2Fin,exp3Debut,exp3Fin) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(sql, (lastIdCV, exp1Title, exp1Resume,  exp2Title, exp2Resume,
                             exp3Title, exp3Resume, exp1Debut, exp1Fin, exp2Debut, exp2Fin, exp3Debut, exp3Fin))
        connection.commit()
        cursor.close()

    with connection.cursor() as cursor:
        sql = 'INSERT INTO formation (IDcv, form1Title, form1Text, form1Debut, form1Fin, form2Title, form2Text,form2Debut,form2Fin,form3Title,form3Text,form3Debut,form3Fin) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(sql, (lastIdCV, form1Title, form1Text, form1Debut, form1Fin, form2Title,
                             form2Text, form2Debut, form2Fin, form3Title, form3Text, form3Debut, form3Fin))
        connection.commit()
        cursor.close()

    with connection.cursor() as cursor:
        sql = 'INSERT INTO hobbies (IDcv, hobby1, hobby2, hobby3) VALUES (%s,%s,%s,%s)'
        cursor.execute(sql, (lastIdCV, hobby1, hobby2, hobby3))
        connection.commit()
        cursor.close()

    with connection.cursor() as cursor:
        sql = 'INSERT INTO language (IDcv,language1,language2,language3) VALUES (%s,%s,%s,%s)'
        cursor.execute(sql, (lastIdCV, language1, language2, language3))
        connection.commit()
        cursor.close()

    with connection.cursor() as cursor:
        sql = 'INSERT INTO skills (IDcv,skill1,skill2,skill3,skill4,skill5) VALUES (%s,%s,%s,%s,%s,%s)'
        cursor.execute(sql, (lastIdCV, skill1, skill2, skill3, skill4, skill5))
        connection.commit()
        cursor.close()

    with connection.cursor() as cursor:
        sql = 'INSERT INTO contact (IDcv,sm1Title,sm1Link,sm2Title,sm2Link,phoneNumber,websiteTitle,websiteLink,email) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(sql, (lastIdCV, sm1Title, sm1Link, sm2Title,
                             sm2Link, phoneNumber, websiteTitle, websiteLink, email))
        connection.commit()
        cursor.close()

    with connection.cursor() as cursor:
        sql = 'INSERT INTO pdfGenerated (contentPdf,idUser) VALUES (%s,%s)'
        cursor.execute(sql, (binaryData, SessionID))
        connection.commit()
        cursor.close()

    return render_template("home.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        with connection.cursor() as cursor:
            sql = "SELECT `IDusers`, `password` FROM `users` WHERE `email`=%s"
            cursor.execute(sql, email)
            users = cursor.fetchall()
            cursor.close()

        if len(users) > 0:
            if bcrypt.checkpw(password, hashed):
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM `users` WHERE `email`=%s"
                    cursor.execute(sql, email)
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


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("home.html")


@app.route('/cvgenerator', methods=["GET", "POST"])
def generateCV():
    return render_template("cvgenerator.html")


def write_file(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)


@app.route('/candidatesAllCv', methods=["GET", "POST"])
def candidatesAllCv():
    with connection.cursor() as cursor:
        sql = "SELECT contentPdf FROM `pdfGenerated` WHERE `IdUser`=%s"
        cursor.execute(sql, session['idUser'])
        allPdfBlob = cursor.fetchall()
        cursor.close()
        fileData = allPdfBlob[0]
        fileData = fileData['contentPdf']

    with open('test.pdf', 'rb') as file:
        fileData = file.read()

    filename = 'test.pdf'

    with tempfile.TemporaryDirectory() as path:
        images_from_path = convert_from_path(
            filename, output_folder=path, last_page=1, first_page=0)

    base_filename = os.path.splitext(os.path.basename(filename))[0] + '.jpeg'
    save_dir = io.BytesIO()

    for page in images_from_path:
        #page.save(os.path.join('templates', base_filename), 'jpeg')
        page.save(save_dir, 'jpeg', filename=base_filename)
        save_dir.seek(0)
        page = base64.b64encode(save_dir.getvalue())

    return render_template('candidatesAllCv.html', page=page.decode('ascii'))


@app.route('/recruitersAllCv', methods=["GET", "POST"])
def recruitersAllCv():
    return render_template("recruitersAllCv.html")


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
            sql = "INSERT INTO users (email, password, status) VALUES (%s,%s,%s)"
            cursor.execute(sql,  (email, hash_password, status))
            connection.commit()
            session['email'] = request.form['email']
            session['status'] = request.form['status']
            cursor.close()
            return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
