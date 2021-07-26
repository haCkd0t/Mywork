from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
import os
import datetime


with open('config.json','r') as q:
    params = json.load(q)["params"]
local_server = "True"


app = Flask(__name__)
app.secret_key = 'badrinath'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = 'TRUE',
    MAIL_USERNAME = params['u-mail'],
    MAIL_PASSWORD = params['p-mail']





)
mail = Mail(app)
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)
class Contactb(db.Model):
    Srn = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    mes = db.Column(db.String(120), nullable=False)

class Posts(db.Model):
    Srn = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(12), nullable=False)



@app.route("/")
def home():
    post = Posts.query.filter_by().all()
    return render_template("index.html",params=params,post=post)


@app.route("/dashboard" ,methods =['GET','POST'])
def login():
    if 'user' in session and session['user'] == params['email']:
        post = Posts.query.filter_by().all()
        return render_template("dashboard.html",params=params,post=post)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email == params['email'] and password == params['password']:
            session['user'] = email
            post = Posts.query.filter_by().all()
            return render_template("dashboard.html",params=params,post=post)
    return render_template("login.html",params=params)


@app.route("/contact", methods = ['GET','POST'])
def contact( ):
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone_num=request.form.get('phone_num')
        mes = request.form.get('mes')
        adds = Contactb(Name=name,email=email,phone_num=phone_num,mes=mes)
        db.session.add(adds)
        db.session.commit()
        mail.send_message( "This Mail is From " +  name,
         sender = email,
         recipients = [params['u-mail']],
         body = mes +"\n" +  phone_num +"\n"  + email

         )



    return render_template("contact.html",params=params)

@app.route("/about")
def about():
    return render_template("about.html",params=params)

@app.route("/edit/<string:Srn>", methods = ['GET', 'POST'])
def edit(Srn):
    if ('user' in session and session['user'] == params['email']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.datetime.now()

            if Srn=='0':
                post = Posts(title=box_title, content=content, tagline=tline, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(Srn=Srn).first()
                post.title = box_title

                post.content = content
                post.tagline = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/post/'+ Srn)
        post = Posts.query.filter_by(Srn=Srn).first()
        return render_template('edit.html', params=params, post=post, Srn=Srn)


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:Srn>", methods = ['GET', 'POST'])
def delete(Srn):
    if ('user' in session and session['user'] == params['email']):
        post = Posts.query.filter_by(Srn=Srn).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')




@app.route("/post/<int:Srn>", methods=['GET'])
def post_route(Srn):
    post = Posts.query.filter_by(Srn=Srn).first()
    return render_template('post.html', params=params,Srn=Srn,post=post)



app.run(debug=True)