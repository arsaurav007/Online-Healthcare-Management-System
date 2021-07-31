from flask import Flask, Markup, render_template, flash, redirect, url_for, session, request, logging 
from flask_mysqldb import MySQL
from wtforms import Form, IntegerField, StringField, TextAreaField, PasswordField, validators, SubmitField
from wtforms.validators import DataRequired
from passlib.hash import sha256_crypt
from functools import wraps
from wtforms.fields.html5 import DateField
from datetime import date
from flask_mail import Mail, Message
#import smtplib
import random
app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'xyz@gmail.com'
app.config['MAIL_PASSWORD'] = 'xyz'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
posta = Mail(app)
#app.secret_key = "super secret key"


app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'k74YQgoO0D'
app.config['MYSQL_PASSWORD'] = 'iWAowcfHMK'
app.config['MYSQL_DB'] = 'k74YQgoO0D'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def index():
	return render_template("homepage.html")

class RegisterForm(Form):
    name = StringField('Name*', [validators.DataRequired(),validators.Length(min=1, max=50)])
    address = StringField('Address', [validators.optional(), validators.length(min=1, max=50)])
    phone = IntegerField('Phone No*', [validators.DataRequired()])
    email = StringField('Email*', [validators.DataRequired(),validators.Length(min=6, max=50), validators.Email()])
    username = StringField('Username*', [validators.DataRequired(),validators.Length(min=4, max=25)])
    sex = StringField('Gender*', [validators.DataRequired(),validators.Length(min=4, max=6)])
    blood = StringField('Blood Group', [validators.optional(), validators.Length(min=2, max=4)])
    age = StringField('Age', [validators.optional()])
    password = PasswordField('Password*', [
        validators.DataRequired(), validators.Length(min=4, max=16),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password*')

class DRegisterForm(Form):
    name = StringField('Name*', [validators.DataRequired(),validators.Length(min=1, max=50)])
    spec = StringField('Field of Specialization*', [validators.DataRequired(),validators.Length(min=1, max=20)])
    address = StringField('Chamber Address*', [validators.DataRequired(),validators.length(min=1, max=50)])
    phone = IntegerField('Phone No*', [validators.DataRequired()])
    fee = IntegerField('Fees*', [validators.DataRequired()])    
    email = StringField('Email*', [validators.DataRequired(),validators.Length(min=6, max=20), validators.Email()])
    username = StringField('Username*', [validators.DataRequired(),validators.Length(min=4, max=10)])
    password = PasswordField('Password*', [
        validators.DataRequired(), validators.Length(min=4, max=16),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password*')

class LoginForm(Form):
    username = StringField('Username*', [validators.DataRequired(),validators.Length(min=4, max=25)])
    password = PasswordField('Password*', [
        validators.DataRequired(), validators.Length(min=4, max=16)
    ])

@app.route('/psign', methods=['GET', 'POST'])
def psign():
	form = RegisterForm(request.form)
	if(request.method == 'POST' and form.validate()):
		name = form.name.data 
		email = form.email.data 
		username = form.username.data 
		phone = form.phone.data 
		sex = form.sex.data 
		address = form.address.data 
		blood = form.blood.data 
		age = form.age.data 
		password = form.password.data

		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM patients WHERE patient_username = %s", [username])
		if result > 0:
			error = 'Username found'
			return render_template('patient_signup.html', error = error, form = form)
		result = cur.execute("SELECT * FROM patients WHERE patient_email = %s", [email])
		if result > 0:
			error = 'email found'
			return render_template('patient_signup.html', error = error, form = form)

		cur.execute("INSERT INTO patients(patient_name, patient_address, patient_phno, patient_email, patient_username, patient_password, patient_bloodgroup, patient_sex, patient_age) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (name, address, phone, email, username, password, blood, sex, age))
		mysql.connection.commit()
		cur.close()

		#FLASH IS NOT WORKING
		#flash('You are now registered and can log in', 'success')
		return redirect(url_for('plog'))
	return render_template('patient_signup.html', form = form)

@app.route('/dsign', methods=['GET', 'POST'])
def dsign():
	form = DRegisterForm(request.form)
	if(request.method == 'POST' and form.validate()):
		name = form.name.data 
		email = form.email.data 
		username = form.username.data 
		phone = form.phone.data 
		address = form.address.data 
		spec = form.spec.data 
		fee = form.fee.data 
		password = form.password.data

		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM doctors WHERE doc_username = %s", [username])
		if result > 0:
			error = 'Username found'
			return render_template('dr_signup.html', error = error, form = form)
		result = cur.execute("SELECT * FROM doctors WHERE doc_email = %s", [email])
		if result > 0:
			error = 'email found'
			return render_template('dr_signup.html', error = error, form = form)


		cur.execute("INSERT INTO doctors(doctor_name ,doctor_spec ,doc_mobileNo ,doc_email ,doc_password ,doc_address ,doc_username ,doc_fees ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (name, spec, phone, email, password, address, username, fee))
		mysql.connection.commit()
		cur.close()

		#FLASH IS NOT WORKING
		#flash('You are now registered and can log in', 'success')
		return redirect(url_for('dlog'))
	return render_template('dr_signup.html', form=form)


@app.route('/plog', methods=['GET', 'POST'])
def plog():
	form = LoginForm(request.form)
	if(request.method == 'POST' and form.validate()):
		username = form.username.data
		password = form.password.data
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM patients WHERE patient_username = %s AND patient_password = %s", [username, password])
		if result == 1:
			return redirect(url_for('user', username=username))
		else:
			error = 'Username/Password Incorrect'
			return render_template('patient_login.html', error = error, form = form)
	return render_template('patient_login.html', form = form)

@app.route('/dlog', methods=['GET', 'POST'])
def dlog():
	form = LoginForm(request.form)
	if(request.method == 'POST' and form.validate()):
		username = form.username.data
		password = form.password.data
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM doctors WHERE doc_username = %s AND doc_password = %s", [username, password])
		if result == 1:
			return redirect(url_for('userd', username=username))
		else:
			error = 'Username/Password Incorrect'
			return render_template('dr_login.html', error = error, form = form)
	return render_template('dr_login.html', form = form)


@app.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
	return render_template('pdashboard.html', username=username)

@app.route('/pout/<username>', methods=['GET', 'POST'])
def pout (username):
	session.pop('username', None)
	return redirect ('/')

@app.route('/dout/<username>', methods=['GET', 'POST'])
def dout (username):
	session.pop('username', None)
	return redirect ('/')

class  BookForm(Form) :
	usernae = StringField('Username*', [validators.DataRequired(),validators.Length(min=4, max=25)])
	startdate = DateField("Enter the date for your appointment*", [validators.DataRequired()])

@app.route('/makeappt/<username>',methods=['GET', 'POST'])
def makeappt(username):
	cursor = mysql.connection.cursor()
	cur = cursor.execute("SELECT doctor_spec FROM doctors")
	ars = cursor.fetchall()
	form2 = BookForm(request.form)
	word = request.form.get("spec", None)
	
	if (request.method == "POST" and not form2.validate()):
		#print(username)
		cursor.execute("SELECT doc_username , doctor_name , doc_address ,doc_fees FROM doctors WHERE doctor_spec = %s" , [word] )
	
	drt = cursor.fetchall()		
	
	if(request.method == "POST" and form2.validate()):
		usernae = form2.usernae.data
		startdate = form2.startdate.data
		cursor.execute("INSERT INTO appointments(doc_username, patient_username ,appt_date) VALUES (%s, %s, %s)",(usernae , username, startdate))
		
		mysql.connection.commit()
		cursor.close()
		#return redirect (url_for('pbook'))
		msg = "appointment booked"
		return render_template('appt_pt.html', username=username, msg = msg, form = form2, tot = ars ,total = drt ,word= word)
		error = "Try again"
		return render_template('appt_pt.html' , username=username, error = error, form= form2, tot = ars ,total = drt ,word= word)

	return render_template('appt_pt.html', username=username, tot = ars ,total = drt ,word= word,form= form2)


@app.route('/pbook/<username>', methods=['GET', 'POST'])
def pbook(username):
	cuh=mysql.connection.cursor()
	duh = cuh.execute("SELECT  a.appointment_id , a.doc_username , d.doctor_spec , d.time FROM appointments a , doctors d WHERE a.doc_username = d.doc_username AND a.patient_username =%s" , [username])
	tuh=cuh.fetchall()
	return render_template('fbook_pt.html',username = username,fet=tuh )

@app.route('/userd/<username>', methods=['GET', 'POST'])
def userd(username):
	return render_template('ddashboard.html', username=username)


@app.route('/apptListdr/<username>', methods=['GET', 'POST'])
def apptListdr(username):
	cur = mysql.connection.cursor()
	res2 = cur.execute("SELECT patient_username, appointment_id, appt_date  FROM appointments a WHERE  a.doc_username= %s" , [username])
	rv = cur.fetchall()
	return render_template('appt_dr.html', data=rv,username=username)


class ResetForm(Form):
	email = StringField('Email*', [validators.DataRequired(),validators.Length(min=6, max=50), validators.Email()])
	username = StringField('Username*', [validators.DataRequired(),validators.Length(min=4, max=25)])


@app.route('/dreset', methods=['GET', 'POST'])
def dreset():
	form = ResetForm(request.form)
	if(request.method == 'POST' and form.validate()):
		email = form.email.data 
		username = form.username.data
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM doctors WHERE doc_username = %s AND doc_email = %s", [username, email])
		if result == 1:
			def get_random_string(length=25,allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
				return ''.join(random.choice(allowed_chars) for i in range(length))
			hashCode = get_random_string()
			cur.execute("INSERT INTO preset(email, username, hashCode) VALUES(%s, %s, %s)", (email, username, hashCode))
			mysql.connection.commit()
			cur.close()  

			msg = Message('Confirm Password Change', sender = 'xyz@gmail.com', recipients = [email])
			msg.body = "Hello,\nWe've received a request to reset your password. If you want to reset your password, click the link below and enter your new password\n http://localhost:5000/" + hashCode
			posta.send(msg)
			message = 'Email Sent'
			return render_template('preset.html', msg = message, form = form)
		else:
			error = 'Username/Email Not Found'
			return render_template('dreset.html', error = error, form = form)
	return render_template('dreset.html', form = form)


@app.route('/preset', methods=['GET', 'POST'])
def preset():
	form = ResetForm(request.form)
	if(request.method == 'POST' and form.validate()):
		email = form.email.data 
		username = form.username.data
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM patients WHERE patient_username = %s AND patient_email = %s", [username, email])
		if result == 1:
			def get_random_string(length=24,allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
				return ''.join(random.choice(allowed_chars) for i in range(length))
			hashCode = get_random_string()
			cur.execute("INSERT INTO preset(email, username, hashCode) VALUES(%s, %s, %s)", (email, username, hashCode))
			mysql.connection.commit()
			cur.close()  

			msg = Message('Confirm Password Change', sender = 'xyz@gmail.com', recipients = [email])
			msg.body = "Hello,\nWe've received a request to reset your password. If you want to reset your password, click the link below and enter your new password\n http://localhost:5000/" + hashCode
			posta.send(msg)
			message = 'Email Sent'
			return render_template('preset.html', msg = message, form = form)
		else:
			error = 'Username/Email Not Found'
			return render_template('preset.html', error = error, form = form)
	return render_template('preset.html', form = form)

class Reset(Form):
    password = PasswordField('Password*', [
        validators.DataRequired(), validators.Length(min=4, max=16),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password*')


@app.route("/<string:hashCode>",methods=["GET","POST"])
def hashcode(hashCode):
	form = Reset(request.form)

	if(request.method == 'POST' and form.validate()):
		password = form.password.data
		
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM preset WHERE hashCode = %s", [hashCode])
		if result:
			if len(hashCode) == 25:
				cur.execute("SELECT email FROM preset WHERE hashCode = %s", [hashCode])
				result_set = cur.fetchall()
				for r in result_set:
					cur.execute("UPDATE doctors SET doc_password=%s WHERE doc_email=%s", [password, r['email']])
					print(r['email'])
				mysql.connection.commit()
				cur.close()
				message = 'Password Changed'
				return render_template('reset.html', msg = message, form = form)				
			cur.execute("SELECT email FROM preset WHERE hashCode = %s", [hashCode])
			result_set = cur.fetchall()
			for r in result_set:
				cur.execute("UPDATE patients SET patient_password=%s WHERE patient_email=%s", [password, r['email']])
				print(r['email'])
			mysql.connection.commit()
			cur.close()
			message = 'Password Changed'
			return render_template('reset.html', msg = message, form = form)
	return render_template('reset.html', form = form)

class ReportForm(Form):
	#patient_name = StringField('Patient Username*', [validators.DataRequired(),validators.Length(min=4, max=25)])
	data = StringField("Patient Data*", [validators.DataRequired()])

@app.route('/reports/<username>', methods=['GET', 'POST'])
def reports(username):
	cur = mysql.connection.cursor()
	sc = cur.execute("SELECT patient_username FROM  appointments WHERE doc_username=%s", [username])
	pl = cur.fetchall()
	word = request.form.get("patient_username", None)
	form = ReportForm(request.form)
	if(request.method == 'POST' and form.validate()):
		data = form.data.data
		result = cur.execute("INSERT INTO reports(prescriptions ,patient_username ,doc_username ) VALUES(%s, %s, %s)", (data, word, username))
		mysql.connection.commit()
		res2 = cur.execute("SELECT patient_username, prescriptions FROM reports WHERE doc_username=%s", [username])
		rv = cur.fetchall()
		return render_template('reports_list.html', data=rv,username=username)
	return render_template('report.html', form=form, pl=pl,username=username)

if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)
