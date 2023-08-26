from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from app import db





class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    avatar = db.Column(db.Integer, default=1)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_enabled = db.Column(db.Boolean, default=True)


class Controller(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(64), unique=True, nullable=False)
    controller_name = db.Column(db.String(128), nullable=False)


def round_to_second():
    dt = datetime.utcnow()
    return dt - timedelta(microseconds=dt.microsecond)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime,  default=round_to_second)
    event = db.Column(db.String(128))
    username = db.Column(db.String(64))






