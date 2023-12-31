from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os

# Instantiate SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    # bootstrap = Bootstrap5(app)
    app.config['SECRET_KEY'] = 'secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'test.db')
    db.init_app(app)
    return app

app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')