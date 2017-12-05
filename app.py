import os
from flask import Flask, request, redirect, url_for, render_template, flash

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
OUTPUT_FOLDER = os.path.join(APP_ROOT, 'static/output')
ALLOWED_EXTENSIONS = set(['yml'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from views import *

#helper functions:

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def merge_dicts(x,y):
    x.update(y)
    return x

if __name__ == '__main__':
    app.run(debug=True)