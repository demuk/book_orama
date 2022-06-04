from flask import render_template, redirect, url_for, request
from app import app


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')
