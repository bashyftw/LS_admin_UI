from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from flask_login.mixins import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from app import app, socketio
from sqlalchemy.exc import IntegrityError
import random
from routes.logs import log_event
from flask_socketio import SocketIO, emit


# socketio = SocketIO(app)

@app.route('/socket')
def socket():
    return render_template('socket.html')

@socketio.on('connect')
def test_connect():
    emit('server_response', {'data': 'Connected'})

@socketio.on('client_event')
def client_msg(msg):
    emit('server_response', {'data': msg['data']})

if __name__ == '__main__':
    socketio.run(app)