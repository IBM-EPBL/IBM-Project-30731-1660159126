from datetime import date

from flask import Flask, render_template, request, session, url_for, redirect
import ibm_db
import os
import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *
import sqlite3 as sql

conn = ibm_db.connect(
    "DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SslServerCertificate=DigiCertGlobalRootCA.crt;UID=gvc94094;PWD=FoHH6J0p5r8hxWSP;",
    "", "")

app = Flask(__name__,template_folder='templates', static_url_path='/static')
app.secret_key = 'jobskill111'


@app.route("/")
@app.route("/home")
def index():
    return render_template('home.html')


@app.route("/about")
def blog():
    return render_template('about.html')


def sendmail(toemail,name):
    message = Mail(
        from_email='jobrecommendator@gmail.com',
        to_emails=toemail,
        subject='Welcome to Job Portal - '+name,
        html_content='<strong>Hi '+name+', Welcome to Job Portal. Hope you will find a suitable job . </strong>')
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)



@app.route("/dashboard")
def dashboard():
    email = session['email']
    vacancies = []
    sql = "SELECT * FROM vacancies ORDER BY VID DESC LIMIT 2"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    vacancy = ibm_db.fetch_assoc(stmt)
    while vacancy != False:
        vacancies.append(vacancy)
        vacancy = ibm_db.fetch_assoc(stmt)
    return render_template("dashboard.html",data=email,vacancies=vacancies)



@app.route("/signup")
def signup():
    return render_template("signup.html")



@app.route("/confirm", methods=['POST', 'GET'])
def confirm():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        skills = request.form.get('skills')
        qualification = request.form.get('qualification')
        sslc = request.form.get('sslc')
        hsc = request.form.get('hsc')

        sql = "SELECT * FROM users WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            return render_template('confirm.html', data="You are already a member, please login using your details")
        else:
            insert_sql = "INSERT INTO users(EMAIL,PASSWORD,FULLNAME,GENDER,DOB,ADDRESS,CITY,STATE,PINCODE,SKILLS,QUALIFICATION,SSLC,HSC) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, email)
            ibm_db.bind_param(prep_stmt, 2, password)
            ibm_db.bind_param(prep_stmt, 3, fullname)
            ibm_db.bind_param(prep_stmt, 4, gender)
            ibm_db.bind_param(prep_stmt, 5, dob)
            ibm_db.bind_param(prep_stmt, 6, address)
            ibm_db.bind_param(prep_stmt, 7, city)
            ibm_db.bind_param(prep_stmt, 8, state)
            ibm_db.bind_param(prep_stmt, 9, pincode)
            ibm_db.bind_param(prep_stmt, 10, skills)
            ibm_db.bind_param(prep_stmt, 11, qualification)
            ibm_db.bind_param(prep_stmt, 12, sslc)
            ibm_db.bind_param(prep_stmt, 13, hsc)
            ibm_db.execute(prep_stmt)
            sendmail(email,fullname)
            return render_template("confirm.html", data="Thank you "+fullname+" for joining with us. Please Login to Continue !")



@app.route("/signin")
def signin():
    return render_template("signin.html")


@app.route("/enter", methods=['POST', 'GET'])
def enter():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')

        sql = "SELECT * FROM users WHERE email =? and  password =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session['email'] = email
            session['uid'] = account['UID']
            return redirect(url_for('dashboard'))
        else:
            return render_template("confirm.html", data="Invalid email or password")


@app.route("/listvacancies")
def listvacancies():
    vacancies = []
    sql = "SELECT * FROM vacancies ORDER BY VID DESC"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    vacancy = ibm_db.fetch_assoc(stmt)
    while vacancy != False:
        vacancy['isapplied'] = isapplied(vacancy['VID'])
        vacancies.append(vacancy)
        vacancy = ibm_db.fetch_assoc(stmt)
    return render_template("listvacancies.html", data=vacancies, text="Posted Vacancies")


def isapplied(vid):
    sql = "SELECT * FROM JOBSAPPLIED WHERE vid =? and  uid =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, vid)
    ibm_db.bind_param(stmt, 2, session['uid'])
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    if account:
        return True
    else:
        return False


@app.route("/searchvacancies", methods=['POST', 'GET'])
def searchvacancies():
    if request.method=='GET':
        vacancies = []
        term = request.args.get('term')
        searchterm = "%"+term+"%";
        sql = "SELECT * FROM vacancies WHERE LCASE(skills) LIKE ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, searchterm)
        ibm_db.execute(stmt)
        vacancy = ibm_db.fetch_assoc(stmt)
        if vacancy:
            while vacancy != False:
                vacancy['isapplied'] = isapplied(vacancy['VID'])
                vacancies.append(vacancy)
             #   print(isapplied(vacancy['VID']))
                vacancy = ibm_db.fetch_assoc(stmt)
            return render_template("listvacancies.html", data=vacancies, text="Search for Vacancies - "+term)
        else:
            return render_template("listvacancies.html", text="No results - "+term)



@app.route("/applyjob", methods=['POST', 'GET'])
def applyjob():
    if request.method=='GET':
        vid = request.args.get('vid')
        rid = request.args.get('rid')
        insert_sql = "INSERT INTO jobsapplied(UID,VID,RID) VALUES (?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, session['uid'])
        ibm_db.bind_param(prep_stmt, 2, vid)
        ibm_db.bind_param(prep_stmt, 3, rid)
        ibm_db.execute(prep_stmt)
        return redirect(url_for('listvacancies'))




@app.route("/profile")
def profile():
    profiledetails = []
    sql = "SELECT * FROM users WHERE uid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session['uid'])
    ibm_db.execute(stmt)
    profile = ibm_db.fetch_assoc(stmt)
    if profile:
        while profile != False:
            profiledetails.append(profile)
            profile = ibm_db.fetch_assoc(stmt)
        return render_template("profile.html", data=profiledetails)
    else:
        return render_template('profile.html')


@app.route("/editprofile")
def editprofile():
    profiledetails = []
    sql = "SELECT * FROM users WHERE uid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session['uid'])
    ibm_db.execute(stmt)
    profile = ibm_db.fetch_assoc(stmt)
    if profile:
        while profile != False:
            profiledetails.append(profile)
            profile = ibm_db.fetch_assoc(stmt)
        return render_template("editprofile.html", data=profiledetails)
    else:
        return render_template('editprofile.html')



@app.route("/updateprofile", methods=['POST', 'GET'])
def updateprofile():
    if request.method=='POST':
        fullname = request.form.get('fullname')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        skills = request.form.get('skills')
        qualification = request.form.get('qualification')
        sslc = request.form.get('sslc')
        hsc = request.form.get('hsc')

        sql = "UPDATE users SET FULLNAME = ?, ADDRESS = ? , CITY = ? , STATE = ? , SKILLS = ? , QUALIFICATION = ? , SSLC = ? , HSC = ? WHERE uid = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, fullname)
        ibm_db.bind_param(stmt, 2, address)
        ibm_db.bind_param(stmt, 3, city)
        ibm_db.bind_param(stmt, 4, state)
        ibm_db.bind_param(stmt, 5, skills)
        ibm_db.bind_param(stmt, 6, qualification)
        ibm_db.bind_param(stmt, 7, sslc)
        ibm_db.bind_param(stmt, 8, hsc)
        ibm_db.bind_param(stmt, 9, session['uid'])
        ibm_db.execute(stmt)
        return redirect(url_for('profile'))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route("/recruiter/recruitersignup")
def recruitersignup():
    return render_template("recruitersignup.html")


@app.route("/recruiter/recruiterconfirm", methods=['POST', 'GET'])
def recruiterconfirm():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        companyname = request.form.get('company')
        website = request.form.get('website')

        sql = "SELECT * FROM recruiter WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            return render_template('confirm.html', data="You are already a member, please login using your details")
        else:
            insert_sql = "INSERT INTO recruiter(FULLNAME,PASSWORD,EMAIL,COMPANYNAME,WEBSITE) VALUES (?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, fullname)
            ibm_db.bind_param(prep_stmt, 2, password)
            ibm_db.bind_param(prep_stmt, 3, email)
            ibm_db.bind_param(prep_stmt, 4, companyname)
            ibm_db.bind_param(prep_stmt, 5, website)
            ibm_db.execute(prep_stmt)
            return render_template("recruiterconfirm.html", data="Thank you "+fullname+" for joining with us. Please Login to Continue !")



@app.route("/recruiter/recruitersignin")
def recruitersignin():
    return render_template("recruitersignin.html")


@app.route("/recruiter/enterrecruiter", methods=['POST', 'GET'])
def enterrecruiter():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')

        sql = "SELECT * FROM recruiter WHERE email =? and  password =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session['recruiteremail'] = email
            session['rid'] = account['RID']
            return redirect(url_for('recruiterdashboard'))
        else:
            return render_template("recruiterconfirm.html", data="Invalid email or password")


@app.route("/recruiter/recruiterdashboard")
def recruiterdashboard():
    recruiteremail = session['recruiteremail']
    return render_template("recruiterdashboard.html",data=recruiteremail)


@app.route("/recruiter/addvacancy")
def addvacancy():
    return render_template("addvacancy.html")


@app.route("/recruiter/vacancyconfirm", methods=['POST', 'GET'])
def vacancyconfirm():
    if request.method=='POST':
        title = request.form.get('title')
        description = request.form.get('description')
        salary = request.form.get('salary')
        company = request.form.get('company')
        skills = request.form.get('skills')
        qualification = request.form.get('qualification')
        dateposted = date.today()
        postedby = session['rid']
        insert_sql = "INSERT INTO vacancies(TITLE,DESCRIPTION,COMPANYNAME,SALARY,DATEPOSTED,POSTEDBY,SKILLS,QUALIFICATION) VALUES (?,?,?,?,?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, title)
        ibm_db.bind_param(prep_stmt, 2, description)
        ibm_db.bind_param(prep_stmt, 3, company)
        ibm_db.bind_param(prep_stmt, 4, salary)
        ibm_db.bind_param(prep_stmt, 5, dateposted)
        ibm_db.bind_param(prep_stmt, 6, postedby)
        ibm_db.bind_param(prep_stmt, 7, skills)
        ibm_db.bind_param(prep_stmt, 8, qualification)
        ibm_db.execute(prep_stmt)
        return redirect(url_for('viewpostedvacancy'))


@app.route("/recruiter/viewpostedvacancy")
def viewpostedvacancy():
    vacancies = []
    sql = "SELECT * FROM vacancies WHERE postedby =? ORDER BY VID DESC"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session['rid'])
    ibm_db.execute(stmt)
    vacancy = ibm_db.fetch_assoc(stmt)
    while vacancy != False:
        vacancies.append(vacancy)
        vacancy = ibm_db.fetch_assoc(stmt)
    return render_template("viewpostedvacancy.html", data=vacancies)


@app.route("/recruiter/viewcandidates", methods=['POST', 'GET'])
def viewcandidates():
    if request.method == 'GET':
        vid = request.args.get('vid')
        profiledetails = []
        userdata = []
        sql = "SELECT * FROM JOBSAPPLIED WHERE VID = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, vid)
        ibm_db.execute(stmt)
        profile = ibm_db.fetch_assoc(stmt)
        if profile:
            while profile != False:
                userdata.append(viewcandidateslist(profile['UID']))
                profiledetails.append(profile)
                profile = ibm_db.fetch_assoc(stmt)
            return render_template("viewcandidates.html", data=userdata)
        else:
            return render_template("viewcandidates.html")



def viewcandidateslist(uid):
    viewcandidates = []
    sql = "SELECT * FROM USERS WHERE UID = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, uid)
    ibm_db.execute(stmt)
    profile = ibm_db.fetch_assoc(stmt)
    if profile:
        while profile != False:
            viewcandidates.append(profile)
            return profile
            profile = ibm_db.fetch_assoc(stmt)
            return profile



@app.route("/recruiter/logout")
def recruiterlogout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)