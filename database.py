from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from app import db, app


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
    name = db.Column(db.String(128), nullable=False)
    led_files_synced = db.Column(db.Boolean,  default=False)
    audio_files_synced = db.Column(db.Boolean,  default=False)
    input_settings_synced = db.Column(db.Boolean,  default=False)
    audio_settings_synced = db.Column(db.Boolean,  default=False)


def round_to_second():
    dt = datetime.utcnow()
    return dt - timedelta(microseconds=dt.microsecond)


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime,  default=round_to_second)
    event = db.Column(db.String(128))
    username = db.Column(db.String(64))


def get_controller_name(ip_address):
    with app.app_context():
        controller = Controller.query.filter_by(address=ip_address).first()
        if controller:
            return controller
        else:
            controller.name = "unknown"
            controller.id = 9999
            return controller







