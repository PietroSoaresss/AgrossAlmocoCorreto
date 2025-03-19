import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
sys.path.append('C:\\Users\\PietroTI\\Documents\\workspace\\almocoBackup')


app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost:5432/registros?client_encoding=UTF8'
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:12345@localhost:5432/registros"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "supersecretkey"


    db = SQLAlchemy(app)