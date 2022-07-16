from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(),primary_key=True)
    user_key=db.Column(db.String(255))
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    profile_pic = db.Column(db.String(), nullable=True, default='default.jpg')
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    libraries = db.relationship('Library', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Library(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    library_cognito = db.Column(db.Boolean())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    books = db.relationship('Book', backref='library', lazy='dynamic')


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    authors = db.Column(db.String(64))
    genre = db.Column(db.String(64))
    year = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    book_cognito = db.Column(db.Boolean())
    book_image = db.Column(db.String(), nullable=True)
    library_id = db.Column(db.Integer, db.ForeignKey('library.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.title)
