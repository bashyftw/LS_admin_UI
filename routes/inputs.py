from flask import render_template
from flask_login import login_required
from database import get_controller_name
from app import app, socketio

from grpc_functions import *

MULTICAST_GROUP = '224.0.0.9'
input_history = []
history_limit = 200
input_states = {}


@socketio.on('input_history_request')
def input_history_request():
    print("input_history_request")
    for input in input_history:
        socketio.emit('input_history', input)


@app.route('/inputs', methods=['GET'])
@login_required
def inputs():
    return render_template('inputs/inputs.html')


def input_callback(data, addr):
    with app.app_context():
        input_cov = parse_input(data, addr)
        if input_cov is None:
            print(data + addr)
            print("Failed to parse message.")
            return

        # Get controller name
        input_cov_dict = input_cov.to_dict()
        controller = get_controller_name(addr[0])
        input_cov_dict['name'] = controller.name
        input_cov_dict['id'] = controller.id
        print(input_cov_dict)

        # Save state
        input_key = f"{input_cov_dict['controller']}_{input_cov_dict['input']}"
        input_states[input_key] = input_cov_dict

        # Save history
        input_history.append(input_cov_dict)
        if len(input_history) > history_limit:
            input_history.pop(0)

        # Sent socket data
        socketio.emit('input', input_cov_dict)


