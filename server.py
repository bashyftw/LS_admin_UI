from threading import Thread
from app import app, db
from flask import Flask, render_template, redirect, url_for
from database import User, Controller
from werkzeug.security import generate_password_hash

from routes.users import *
from routes.login import *
from routes.controllers import *
from routes.inputs import *
from routes.logs import *
# from routes.socket import *
# # from routes.upd import *
from routes.multicast import *
from routes.files import *


@app.context_processor
def inject_details():
    controllers = Controller.query.all()
    page_data = {
        "title": "LightSculptor",
        "controller_names": controllers
    }
    return page_data

@app.route('/')
@login_required
def index():
    return render_template('index.html')

# @socketio.on('connect')
# def test_connect():
#     print("connect")
#     pass


def handle_audio():
    with app.app_context():

        start = True
        current_time = 0
        while True:
            if start:
                time.sleep(5)
                current_time = int(time.time())  # Get the current timestamp
                socketio.emit('audio data',{'audio_file': 'Audio File1', 'start_time': current_time + 5, 'duration': 6, 'speakers': [1, 2, 3]})
                start = False
            else:
                time.sleep(8)
                socketio.emit('audio data',
                     {'audio_file': 'Audio File1', 'start_time': current_time + 5, 'removed': True})
                start = True


@app.errorhandler(404)
def page_not_found(e):
    return render_template('admin/404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin', password=generate_password_hash('admin', method='pbkdf2:sha256'), is_admin=True)
            db.session.add(user)
            db.session.commit()
            # Create some dummy data
            dummy_data = [
                {"address": "192.168.1.1", "controller_name": "Controller 1"},
                {"address": "192.168.1.2", "controller_name": "Controller 2"},
                {"address": "192.168.1.3", "controller_name": "Controller 3"},
                # Add more dictionaries for more dummy data
            ]

            # Add the dummy data to the database
            for data in dummy_data:
                controller = Controller(address=data["address"], controller_name=data["controller_name"])
                db.session.add(controller)

            # Commit the changes to the database
            db.session.commit()
    # thread = Thread(target=handle_audio)
    # thread.start()
    # multicast_listener(5555, input_udp)
    multicast_listener(5555, input_udp2)
    multicast_listener(6666, led_udp)
    multicast_listener(7777, audio_udp)
    socketio.run(app, debug=True, host="0.0.0.0", port=8081)
    # app.run(debug=True, host="0.0.0.0", port=8081)

