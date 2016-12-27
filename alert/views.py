from flask import render_template, flash, redirect, request, url_for
from alert import app, db
from models import *
from urllib2 import urlopen


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')
