from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_mysqldb import MySQL, MySQLdb
import bcrypt
import datetime
import docx2txt
import B as b
import C as c
from flask.helpers import make_response
import json
import os
import random
import uuid
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import re



app = Flask(__name__)
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'resumeevaluation'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'rutujasp.1002@gmail.com'
app.config['MAIL_PASSWORD'] = 'GetSetGo@2020'

mail = Mail(app)
mysql = MySQL(app)


@app.route('/')
def home():
    return render_template("Home.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        messages = ['Successfully Registered','User already exists']
        name = request.form['name']
        email = request.form['email']
        f = request.files['CVFile'] 
        f.save(f.filename)
        cvfile = convertToBinary(f.filename)
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
       
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM allusers")
        result = cur.fetchall()
        user = []
        for i in result:
            user.append(i[2])    

        if email not in user:  
            cur.execute("INSERT INTO allusers (name, email, password) VALUES (%s,%s,%s)",(name,email,hash_password,))
            mysql.connection.commit()
        
            cur.execute("INSERT INTO candidate (UserName, Email, Password) VALUES (%s,%s,%s)",(name,email,hash_password,))
            mysql.connection.commit()

            cur.execute("SELECT CandidateID FROM candidate WHERE UserName = %s",(name,))
            cid = cur.fetchone()
            newid = cid[0]  
            data = getFile(f.filename)
            if data != None or data != " ":
                cur.execute("INSERT INTO cv_table(CandidateID,CV,CvData) VALUES(%s,%s,%s)",(cid,cvfile,data,))
                mysql.connection.commit()

                insertInfo(newid)
                message = messages[0]
                flash("Reistered Successfully",'success')
                return redirect(url_for('home'))

            else:
                flash("Something went wrong!!",'error')  
                return redirect(url_for('home'))

        message = messages[1]
        return message

@app.route('/forgot' , methods=["POST","GET"])
def forgot():
    if 'login' in session:
        return redirect('/')
    if request.method == "POST":
        email = request.form["email"]
        token = str(uuid.uuid4())
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE EmailID=%s",[email])
        if result > 0:
            cur.execute("SELECT UserName FROM users WHERE EmailID=%s",[email])
            data = cur.fetchone()

            msg = Message(subject="Forgot Password Request", sender="admin@gmail.com", recipients=[email])
            msg.body = render_template("sent.html", token=token, data=data)
            mail.send(msg)

            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET Token=%s WHERE EmailID=%s",[token, email])
            cur.close()
            flash("Email already sent to your email",'success')
            return redirect('/forgot')
        else:
            flash("Email do not match",'danger')
    return render_template('forgot.html')

@app.route('/reset/<token>' , methods=["POST","GET"])
def reset(token):
    if 'login' in session:
        return redirect('/')
    if request.method =="POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        token1 = str(uuid.uuid4())
        if password != confirm_password:
            flash("Password do not match",'danger')
            return redirect('reset')
        password = bcrypt.generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE Token=%s", [token])
        user = cur.fetchone()
        if user:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET Token=%s, Password=%s WHERE Token=%s",[token1, password, token])
            mysql.connection.commit()
            cur.close()
            flash("Your password Successfully Updated",'success')
            return redirect('/home')
        else:
            flash("Your token is invalid",'danger')
            return redirect('/home')
    return render_template('Reset1.html')

@app.route('/CandidateLogin',methods=["GET","POST"])
def CandidateLogin():
    message = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM allusers WHERE email=%s",(email,))
        user = curl.fetchone()
        
        curl.execute("SELECT CandidateID FROM candidate WHERE Email= %s",(email,))
        cid = curl.fetchone()
        #newid = cid.get('CandidateID')

        if user is not None:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session['name'] = user['name']
                session['CandidateID'] = cid
                return redirect(url_for('CandidateDashboard'))
            else:
                flash(message="Invalid User credentials",category='warning')
                return render_template("Home.html")
        else:
            flash(message="User Not found",category='error')
            return render_template("Home.html")
    else:
        return render_template("Home.html")

@app.route('/AdminLogin',methods=["GET","POST"])
def AdminLogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        uname = "Admin"
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM allusers WHERE name=%s AND email=%s",(uname,email,))
        user = curl.fetchone()
        curl.close()
        if user is not None:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                return redirect(url_for('Admindashboard'))
            else:
                return "Error password and email not match"
        else:
            return "Error U are not Admin Sorry"
    else:
        return render_template("AdminLogin.html")

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("Home.html")

@app.route('/Admindashboard')
def Admindashboard():
    count = getCountAdimin()
    return render_template("Admindashboard.html", Counts = count)

@app.route('/JobsTable')
def AdminJobs():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM jobprofile")
    data = cur.fetchall()
    cur.close()
    return render_template('AdminJobs.html', jobprofile=data )

@app.route('/insert', methods = ['POST','GET'])
def InsertJob():
    if request.method == "POST":
        return render_template("AdminEdit.html")
        flash("Data Inserted Successfully")
        ProfileName = request.form['ProfileName']
        ProfileDescription = request.form['ProfileDescription']
        Vacancies = request.form['Vacancies']
        Qualifications = request.form['Qualifications']
        Skills = request.form['Skills']
        Location = request.form['Location']
        AverageSalary = request.form['AverageSalary']
        ApplicationOpeningdate = request.form['ApplicationOpeningdate']
        ApplicationClosingdate = request.form['ApplicationClosingdate']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO jobprofile (ProfileName, ProfileDescription, Vacancies, Qualifications, Skills, Location, AverageSalary, ApplicationOpeningdate, ApplicationClosingdate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (ProfileName, ProfileDescription, Vacancies, Qualifications, Skills, Location, AverageSalary, ApplicationOpeningdate, ApplicationClosingdate))
        mysql.connection.commit()
        return redirect(url_for('AdminJobs'))

@app.route('/update/<string:p_name>',methods=['POST','GET'])
def UpdateJob(p_name):
    if request.method == 'POST':
        id_data = request.form['id']
        ProfileName = request.form['ProfileName']
        ProfileDescription = request.form['ProfileDescription']
        Vacancies = request.form['Vacancies']
        Qualifications = request.form['Qualifications']
        Skills = request.form['Skills']
        Location = request.form['Location']
        AverageSalary = request.form['AverageSalary']
        ApplicationOpeningdate = request.form['ApplicationOpeningdate']
        ApplicationClosingdate = request.form['ApplicationClosingdate']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE jobprofile
               SET ProfileName=%s, ProfileDescription=%s, Vacancies=%s, Qualifications=%s, Skills=%s, Location=%s, AverageSalary=%s, ApplicationOpeningdate=%s, ApplicationClosingdate=%s
               WHERE id=%s
            """, (ProfileName, ProfileDescription, Vacancies, Qualifications, Skills, Location, AverageSalary, ApplicationOpeningdate, ApplicationClosingdate, id_data))
        flash("Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('AdminJobs'))

@app.route('/delete/<string:id_data>', methods = ['GET'])
def DeleteJob(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM jobprofile WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('AdminJobs'))

# to download the resume
@app.route('/Candidates',methods=['GET','POST'])
def AdminView():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM candidateapplication")
    result = cur.fetchall()
    return render_template("AdminVerify.html",applications = result)
    
@app.route('/CandidateView/<int:cid>')
def CandidateView(cid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM candidateinfo WHERE CandidateID=%s",(cid,))
    result = cur.fetchall()
    for i in result:
        name = i[1]
        phone = i[2]
        email = i[3]
        edu = json.loads(i[5])   # list type
        skill = json.loads(i[7])   # string(json) type
                
    final_info = [name,email,phone,edu,skill]
    return render_template("CandidateProfile.html",final_info=final_info)

@app.route('/AdminVerify/<int:cid>',methods=['GET','SET'])
def AdminVerify(cid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM candidateapplication WHERE CandidateID=%s",(cid,))
    result = cur.fetchone()
    status = 'Verified'
    if result[5] != None:
        cur.execute("UPDATE candidateapplication SET VerificationStatus=%s WHERE CandidateID=%s",(status,cid,))
        mysql.connection.commit()
        #print("status updated as verified")
        return redirect(url_for('AdminView'))
    return redirect(url_for('AdminView'))

@app.route('/AdminReport')
def AdminReport():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT * FROM candidateapplication")
    result = list(cur.fetchall())
    selection = None
    report = []
    for i in result:
        if i[6] == 'Selected':
            selection = 'Selected'
        elif i[6] == None or i[6] == '':
            if i[4] == 'Not Eligible':
                selection = 'Not Selected'
            else:
                selection = 'Status Pending'

        job_id = i[2]
        cur.execute("SELECT ProfileName FROM jobprofile WHERE ProfileId=%s",(job_id,))
        job_name = list(cur.fetchone())
        j = list(i)
        j[2] = job_name[0]
        j.insert(6,selection)
        report.append(j)

    my_graph = plot_graph()
    return render_template('AdminReport1.html',report = report,file = my_graph)

@app.route('/DomainReport',methods=['GET','POST'])
def DomainReport():
    cur = mysql.connection.cursor()
    if request.method == 'POST':

        status = 'Verified'
        info = []
        application = []
        cur.execute("SELECT * FROM candidateapplication WHERE VerificationStatus=%s",(status,))
        result = cur.fetchall()
        for i in result:
            app_id=i[0]
            cid = i[1]
            job_id = i[2]

            cur.execute("SELECT * FROM candidateinfo WHERE CandidateID=%s",(cid,))
            ans = cur.fetchone()
            skill_rank = ans[8]
            domain = ans[9]

            info = [app_id,cid,job_id,domain]
            application.append(info)

        my_graph = plot_graph()
        return render_template('AdminReport2.html',applications = application,file = my_graph) 
    
    my_graph = plot_graph()
    return redirect(url_for('AdminReport'))

@app.route('/Select/<int:cid>/<int:app_id>')
def Select(cid,app_id):
    cur = mysql.connection.cursor()
    status = 'Selected'
    cur.execute("UPDATE candidateapplication SET SelectionStatus=%s WHERE CandidateID=%s AND ApplicationID=%s",(status,cid,app_id))
    mysql.connection.commit()
    return redirect(url_for('DomainReport'))

@app.route('/Reject/<int:cid>/<int:app_id>')
def Reject(cid,app_id):
    cur = mysql.connection.cursor()
    status = 'Not Selected'
    cur.execute("UPDATE candidateapplication SET SelectionStatus=%s WHERE CandidateID=%s AND ApplicationID=%s",(status,cid,app_id))
    mysql.connection.commit()
    return redirect(url_for('DomainReport'))


@app.route('/SendMail/<int:cid>')
def SendMail(cid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM candidateinfo WHERE CandidateID=%s",(cid,))
    result1 = cur.fetchone()
    name = result1[1]
    email = result1[3]
    criteria = result1[6]

    cur.execute("SELECT * FROM candidateapplication WHERE CandidateID=%s",(cid,))
    result2 = cur.fetchone()
    app_id = result2[0]
    status = result2[6]

    if criteria == 'Eligible' or criteria == 'Need Verification':
        if status == 'Selected':
            data = [name,cid,app_id,email]
            msg = Message(subject="Resume Evaluation Feedback", sender="admin@gmail.com", recipients=[email])
            msg.body = render_template("Selected.html", data=data)
            mail.send(msg)
            #print("Mail sent successfully")
            return redirect(url_for('AdminReport'))

        elif status == '' or status == None:
            data = [name,cid,app_id,email]
            msg = Message(subject="Resume Evaluation Feedback", sender="admin@gmail.com", recipients=[email])
            msg.body = render_template("Rejected.html", data=data)
            mail.send(msg)
            #print("Mail sent successfully")
            return redirect(url_for('AdminReport'))

    elif criteria == 'Not Eligible' or criteria == None:
        data = [name,cid,app_id,email]
        msg = Message(subject="Resume Evaluation Feedback", sender="admin@gmail.com", recipients=[email])
        msg.body = render_template("Rejected.html", data=data)
        mail.send(msg)
        cur.execute("DELECT FROM candidateapplication WHERE CandidateID=%s",(cid,))
        #print("Application removed successfully")
        #print("3")
        return redirect(url_for('AdminView'))

@app.route('/Candidatedashboard')
def CandidateDashboard():
    count = getCountCandidate()
    return render_template('CandidateDashboard.html',Counts = count)

@app.route('/CandidateJobs', methods = ['GET','POST'])
def CandidateJobs():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM jobprofile")
    data = cur.fetchall()
    cur.close()
    return render_template('CandidateJobs.html', jobs = data)

@app.route('/CandidateApply/<ProfileName>')
def CandidateApply(ProfileName):
    cid = getSession()
    today = datetime.datetime.now().date()
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM candidateinfo WHERE CandidateID=%s",(cid,))
    result1 = cur.fetchone()
    criteria = result1[6]
    #print(criteria)

    cur.execute("SELECT * FROM jobprofile WHERE ProfileName=%s",(ProfileName,))
    job = cur.fetchone()
    job_id = job[0]
    #print(job_id)
    ##print(job[1],'\n',job[9])

    cur.execute("SELECT * FROM candidateapplication where CandidateID=%s",(cid,))
    result = cur.fetchone()
    #print(result)

    if result!=None:
        if result[2]==job_id:
            flash(message="You have already applied for this profile.",category='warning')
        else:
            cur.execute("""INSERT INTO candidateapplication(CandidateID,JobID,Applyingdate,Eligibility) 
            VALUES (%s,%s,%s,%s)""",(cid,job_id,today,criteria,))
            mysql.connection.commit()
            flash(message="Successfully applied!!",category='success')

    else:
        cur.execute("""INSERT INTO candidateapplication(CandidateID,JobID,Applyingdate,Eligibility) 
        VALUES (%s,%s,%s,%s)""",(cid,job_id,today,criteria,))
        mysql.connection.commit()
        flash(message="Successfully applied!!",category='success')     
    
    info = getInfo(cid)
    name = info[0]
    data = info[6]
    
    domain = None
    if criteria == 'Eligible' or criteria == 'Need Verification':
        domain = b.Classifier(name,data)
    elif criteria == 'Not Eligible':
        domain = 'Not applicable'

    cur.execute("UPDATE candidateinfo SET Domain=%s WHERE CandidateID=%s",(domain,cid,))
    mysql.connection.commit()
    flash(message="Successfully applied!!",category='success')
    return redirect(url_for('CandidateJobs')) 

@app.route('/MyApplications')
def MyApplications():
    cid = getSession()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM candidateapplication WHERE CandidateID=%s",(cid,))
    result = cur.fetchall()

    applications = []
    for i in result:
        app_id = i[0]
        job_id = i[2]
        cur.execute("SELECT * FROM jobprofile WHERE ProfileID=%s",(job_id,))
        job_name = cur.fetchone()
        date = i[3]
        status = i[5]
        if status == None or status=='' or status == 0 or status == '0':
            status = 'Not Verified'
    
        appln = [app_id,job_name[1],date,status]
        applications.append(appln)
    
    ##print(applications)
    return render_template('CandidateApplication.html',applications = applications)

@app.route('/CandidateReport')
def CandidateReport():
    cid = getSession()
    applications=[]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM candidateapplication WHERE CandidateID=%s",(cid,))
    ans = cur.fetchall()
    for result in ans:
        app_id=result[0]
        ver_status = result[5]
        if ver_status == None or ver_status=='' or ver_status == 0 or ver_status == '0':
            ver_status = 'Not Verified'
        sel_status = result[6]
        if sel_status == None or sel_status=='' or sel_status == 0 or sel_status == '0':
            sel_status = 'Not Selected'

        application =  [cid,app_id,ver_status,sel_status]
        applications.append(application)

    
    candidates=[]
    cur.execute("SELECT * FROM candidate WHERE CandidateID=%s",(cid,))
    result = cur.fetchone()
    name = result[1]
    #print(name)
    

    cur.execute("SELECT * FROM cv_table WHERE CandidateID=%s",(cid,))
    result2 = cur.fetchone()
    data = result2[3] 

    info = [name,data] 
    #print(info)
    candidates.append(info)

    #print(candidates)
    graph_location = c.getGraph(candidates)
    #print("graph changed")
    return render_template('CandidateReport.html',applications = applications,file=graph_location)


@app.route('/CandidateProfile')
def CandidateProfile():
    cid = getSession()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM candidateinfo WHERE CandidateID=%s",(cid,))
    result = cur.fetchall()
    for i in result:
        name = i[1]
        phone = i[2]
        email = i[3]
        edu=json.loads(i[5]) 
        skill = json.loads(i[7])   # list type
    

    final_info = [name,email,phone,edu,skill]
    ##print(final_info)
    return render_template("CandidateProfile2.html",final_info=final_info)

def getFile(filename):
    txt = ['.txt','.doc','.docx']
    pdf = ['.pdf']
    file_name = os.path.splitext(filename)
    if file_name[1] in txt:
        data = b.extract_text_from_doc(filename)
    else:
        data = b.extract_text_from_pdf(filename)

    return data

def insertInfo(newid):
    info = getInfo(newid)
    name = info[0]
    email = info[1]
    phone = info[2]
    edu = info[3]
    criteria = info[4]
    quali = json.dumps(edu)
    skill = json.dumps(info[5])
   
    cur = mysql.connection.cursor()
    cur.execute("UPDATE candidate SET CandidateName=%s WHERE CandidateID=%s",(name,newid,))
    cur.execute("""INSERT INTO candidateinfo(CandidateID,CandidateName,ContactNo,EmailID,Qualifications,CriteriaEligibility,Skills)
    VALUES(%s,%s,%s,%s,%s,%s,%s)""",(newid,name,phone,email,quali,criteria,skill,))
    mysql.connection.commit()    
    #print("Added info successfully")

def convertToBinary(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)

def getScore(final_skills):
    score = 0
    score_list=[]
    status = "Verified"
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM candidateapplication WHERE VerificationStatus=%s",(status,))
    result = cur.fetchall()
    for j in result:
        cid = j[1]
        cur.execute("SELECT * FROM cv_table WHERE CandidateID=%s",(cid,))
        result=cur.fetchone()
        resume = result[3]
        
        score = int(b.Resume_Ranker(resume,final_skills)) 
        score_list.append(score)
        print(score_list)
        cur.execute("UPDATE candidateinfo SET SkillRank=%s WHERE CandidateID=%s",(score,cid,))
        mysql.connection.commit()
        #print("Updated")

def getSkillCount(r_skills,c_skills):
    d={}    
    count=0
    for i in c_skills:
        c=0
        if i in r_skills:
            c+=1
            d[i]=c

    
    count=count+len(d)
    return count
        
def getInfo(cid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cv_table WHERE CandidateID=%s",(cid,))
    result = cur.fetchone()
    data = result[3]
    name = b.extract_name(data)
    contact = b.extract_mobile_number(data)
    email = b.extract_email(data)
    quali = b.extract_education(data)
    criteria = b.Labeler(quali,data)
    skills = b.extract_skills(data)
    newSkills = b.getCategory(skills)
    
    info = [name,email,contact,quali,criteria,newSkills,data]
    ##print(info)
    return info

def getCountAdimin():
    Counts = []
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM jobprofile")
    jobs = cur.fetchone()
    Counts.append(jobs)  #0

    cur.execute("SELECT COUNT(*) FROM candidate")
    candidates = cur.fetchone()
    Counts.append(candidates) #1

    cur.execute("SELECT COUNT(*) FROM candidateapplication")
    applications = cur.fetchone()
    Counts.append(applications) #2

    status = 'Verified'
    cur.execute("SELECT COUNT(*) FROM candidateapplication WHERE VerificationStatus=%s",(status,))
    verified = cur.fetchone()
    Counts.append(verified) #3

    selection = "Selected"
    cur.execute("SELECT COUNT(*) FROM candidateapplication WHERE SelectionStatus=%s",(selection,))
    selected = cur.fetchone()
    Counts.append(selected) #4

    out = [item for t in Counts for item in t] 
    ##print(out)
    return out

def getCountCandidate():
    Counts = []
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM jobprofile")
    jobs = cur.fetchone()
    Counts.append(jobs)  #0

    cid = getSession()
    cur.execute("SELECT COUNT(DISTINCT ApplicationID) FROM candidateapplication WHERE CandidateID=%s",(cid,))
    applied_jobs = cur.fetchone()
    Counts.append(applied_jobs) #1

    status = 'Verified'
    cur.execute("SELECT COUNT(DISTINCT ApplicationID) FROM candidateapplication WHERE VerificationStatus=%s AND CandidateID=%s",(status,cid,))
    verified = cur.fetchone()
    Counts.append(verified) #2
    ##print(Counts)

    out = [item for t in Counts for item in t] 
    ##print(out)
    return out

def getSession():
    resp = session.get('CandidateID')
    newid = resp.get('CandidateID')
    ##print(newid)
    return newid

def plot_graph():
    #status = 'Verified'
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT CandidateID FROM candidateapplication")
    result=cur.fetchall()
    #print(ID_list)
    candidates = []
    info = []
    #print(result)
    for i in result:
        cid=i[0]
        cur.execute("SELECT * FROM candidate WHERE CandidateID=%s",(cid,))
        result1 = cur.fetchone()
        name = result1[1]
        #print(name)

        cur.execute("SELECT * FROM cv_table WHERE CandidateID=%s",(cid,))
        result2 = cur.fetchone()
        data = result2[3]

        info = [name,data] 
        #print(info)

        candidates.append(info)

    #print(candidates)
    graph_location = c.getGraph(candidates)
    return graph_location

@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response

if __name__ == "__main__":
    app.secret_key = "^A%DJAJU^JJ123"
    app.run(debug=True)
    