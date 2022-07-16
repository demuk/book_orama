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
from werkzeug.utils import secure_filename
import uuid as uuid
import os
import secrets

UPLOAD_FOLDER = 'app/static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/home')
@login_required
def home():
    library = Library.query.all()
    private_lib=Library.query.filter_by(library_cognito=1)
    return render_template('index.html', library=library,private_lib=private_lib)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/book/<int:id>')
@login_required
def book(id):
    book = Book.query.get(id)
    book_image = url_for('static', filename='bookimg/' + book.book_image)
    return render_template('book.html', book=book, book_image=book_image)


@app.route('/library/<int:id>')
@login_required
def library(id):
    library = Library.query.get(id)
    count = Book.query.filter_by(library_id=id).count()
    user = User.query.all()
    return render_template('library.html', library=library, count=count)

@app.route('/library_privacy/<int:id>')
@login_required
def library_privacy(id):
    library = Library.query.get(id)
    if library.library_cognito == 0:
        library.library_cognito = 1
    else :
        library.library_cognito = 0
    db.session.commit()
    return redirect(url_for('library',id=id))


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
    profile_pic = url_for('static', filename='img/' + user.profile_pic)
    return render_template('profile.html', user=user, time=time, profile_pic=profile_pic)


def save_profile_pic(profile_pic):
    random_hex = secrets.token_hex(8)
    _, f_text = os.path.splitext(profile_pic.filename)
    picture_fn = random_hex + f_text
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
    profile_pic.save(picture_path)
    return picture_fn


@app.route('/editprof/<int:id>', methods=['POST', 'GET'])
@login_required
def editprof(id):
    user = User.query.get(id)
    if request.method == 'POST':
        if request.files:
            image = request.files['profile_pic']
            image_file = save_profile_pic(image)
            user.profile_pic = image_file
            user.username = request.form['username']
            user.first_name = request.form['first_name']
            user.last_name = request.form['last_name']
            user.email = request.form['email']
            user.about_me = request.form['bio']
            db.session.commit()
            flash('profile changed')
            return redirect(url_for('user', id=id))
    return render_template('editprof.html', user=user, id=id)


@app.route('/add_library', methods=['GET', 'POST'])
@login_required
def add_lib():
    if request.method == 'POST':
        name = request.form['lib_name']
        location = request.form['lib_location']
        user_id = current_user.id
        library_cognito = int(request.form['library_cognito'])
        library = Library(name=name, location=location, user_id=current_user.id, library_cognito=library_cognito)
        db.session.add(library)
        db.session.commit()
        flash('library added successfully')
        return redirect(url_for('home'))
    return render_template('addlib.html')


def save_book_img(book_image):
    random_hex = secrets.token_hex(8)
    _, f_text = os.path.splitext(book_image.filename)
    picture_fn = random_hex + f_text
    picture_path = os.path.join(app.root_path, 'static/bookimg', picture_fn)
    book_image.save(picture_path)
    return picture_fn


@app.route('/addbook', methods=['POST', 'GET'])
@login_required
def addbook():
    libraries = Library.query.filter_by(user_id=current_user.id)
    if request.method == 'POST':
        if request.files:
            image = request.files['book_image']
            image_file = save_book_img(image)
            book_image = image_file
            book = Book(title=request.form['title'], authors=request.form['authors'],
                        genre=request.form['genre'], year=request.form['year'], library_id=request.form['lib_id'],
                        book_image=book_image)
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully!')
            return redirect(url_for('library', id=request.form['lib_id']))
    return render_template('addbook.html', libraries=libraries)


@app.route('/logout')
@login_required
def logout():
    current_user.last_seen = datetime.utcnow()
    db.session.commit()
    logout_user()
    return redirect(url_for('home'))
