import base64
from datetime import datetime
import os

from flask import render_template, redirect, url_for, request, flash
from werkzeug.urls import url_parse
from app import app, db
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Book, Library
from app.forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/')
@app.route('/home')
@login_required
def home():
    library = Library.query.all()
    return render_template('index.html', library=library)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        if request.files:
            image = request.files['image']
            bytez = image.read()
            user = User(username=request.form['username'], email=request.form['email'],
                        password_hash=generate_password_hash(request.form['password']))
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user:
            if check_password_hash(user.password_hash, request.form['password']):
                login_user(user, remember=True)
            return redirect(url_for('home'))
        flash('invalid Username or Password')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/user/<int:id>')
@login_required
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    time = datetime.utcnow()

    return render_template('profile.html', user=user, time=time)


app.config['IMAGE_UPLOADS'] = '/home/kiptoo/Desktop/book_orama/app/static/img'


@app.route('/editprof/<int:id>', methods=['POST', 'GET'])
@login_required
def editprof(id):
    user = User.query.get(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.about_me = request.form['bio']
        db.session.commit()
        flash('profile changed')
        return redirect(url_for('user', id=id))
    return render_template('editprof.html', user=user)


@app.route('/add_library', methods=['GET', 'POST'])
@login_required
def add_lib():
    if request.method == 'POST':
        name = request.form['lib_name']
        location = request.form['lib_location']
        user_id = current_user.id
        library = Library(name=name, location=location, user_id=current_user.id)
        db.session.add(library)
        db.session.commit()
        flash('library added successfully')
        return redirect(url_for('home'))
    return render_template('addlib.html')


@app.route('/addbook', methods=['POST', 'GET'])
@login_required
def addbook():
    if request.method == 'POST':
        if request.files:
            image = request.files['image']
            bytez = image.read()
            book = Book(title=request.form['title'], authors=request.form['authors'],
                        genre=request.form['genre'], year=request.form['year'])
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully!')
            return redirect(url_for('home'))
    return render_template('addbook.html')


@app.route('/logout')
@login_required
def logout():
    current_user.last_seen = datetime.utcnow()
    db.session.commit()
    logout_user()
    return redirect(url_for('home'))
