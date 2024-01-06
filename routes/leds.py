from flask import render_template
from flask_login import login_required
from database import get_controller_name
from app import app, socketio

from grpc_functions import *

MULTICAST_GROUP = '224.0.0.9'
leds_history = []
history_limit = 200

@socketio.on('leds_history_request')
def input_history_request():
    print("leds_history_request")
    for leds in leds_history:
        socketio.emit('leds_history', leds)

@app.route('/leds', methods=['GET'])
@login_required
def leds():
    return render_template('leds/leds.html')


def leds_callback(data, addr):
    with app.app_context():
        leds_cov = parse_led(data, addr)
        if leds_cov is None:
            print(data + addr)
            print("Failed to parse message.")
            return

        # Get controller name
        leds_cov_dict = leds_cov.to_dict()
        controller = get_controller_name(addr[0])
        leds_cov_dict['name'] = controller.name
        leds_cov_dict['id'] = controller.id
        print(leds_cov_dict)

        # Save history
        leds_history.append(leds_cov_dict)
        if len(leds_history) > history_limit:
            leds_history.pop(0)

        # Sent socket data
        socketio.emit('leds', leds_cov_dict)
