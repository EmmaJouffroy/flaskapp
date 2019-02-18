from flask import Flask, request, render_template, make_response, send_file, url_for, session, redirect
import pymysql
import cStringIO
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import mysql.connector
import os
import bcrypt

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
    img = request.form['img']
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
    exp1Text = request.form['exp1Resume']
    exp2Title = request.form['exp2Title']
    exp2Text = request.form['exp2Resume']
    exp3Title = request.form['exp3Title']
    exp3Text = request.form['exp3Resume']
    language1 = request.form['language1']
    language2 = request.form['language2']
    language3 = request.form['language3']
    choicesskills = request.values.getlist('skills[]')
    choiceshobbies = request.values.getlist('hobbies[]')
    phoneNumber = request.form['phoneNumber']
    email = request.form['email']
    websiteTitle = request.form['websiteTitle']
    websiteLink = request.form['websiteLink']
    sm1Title = request.form['sm1Title']
    sm1Link = request.form['sm1Link']
    sm2Title = request.form['sm2Title']
    sm2Link = request.form['sm2Link']
    status = request.form['status']

    print(img)

    output = cStringIO.StringIO()
    doc = SimpleDocTemplate("test.pdf", pagesize=letter)
    Story = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    ptext = """<font size=12>%s</font>""" % (title)
    p1text = """<font size=15>%s</font>""" % (resume)
    p2text = """<font size=10>%s</font>""" % (email)
    p3text = """<font size=9>%s</font>""" % (sm2Title)
    p4text = """<font size=6>%s</font>""" % (status)

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
    return send_file('test.pdf', as_attachment=True)


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
                    session['status'] = str(user['status'])
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


@app.route('/candidatesAllCv', methods=["GET", "POST"])
def candidatesAllCv():
    return render_template("candidatesAllCv.html")


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
