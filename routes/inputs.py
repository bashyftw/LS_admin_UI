from flask import render_template, jsonify
from flask_login import login_required
from database import Controller
from app import app, socketio
import random

import sys

from grpc_stuff.grpc_functions import *

MULTICAST_GROUP = '224.0.0.9'

sys.path.append('../grpc_stuff/proto')
from grpc_stuff.proto import inputs_pb2

latest_values = []
input_states = {}


def input_callback(data, addr):
    with app.app_context():
        input_cov = parse_input(data, addr)
        if input_cov is None:
            print("Failed to parse message.")
            return

        print(input_cov.to_dict())
        socketio.emit('input_data', input_cov.to_dict())


@app.route('/inputs', methods=['GET'])
@login_required
def inputs():
    return render_template('inputs/inputs.html')


@app.route('/get_inputs/<int:controller_id>', methods=['GET'])
def get_controller_statuses(controller_id):
    # Replace this with your actual logic to get the controller statuses
    controller_statuses = [random.choice([True, False]) for _ in range(16)]
    return jsonify(controller_statuses)


@socketio.on('input_history')
def input_history():
    print("input_states", input_states)
    socketio.emit('input_states', {'states': input_states})
    for value in latest_values:
        socketio.emit('input_value', {'data': value})


def get_controller_by_ip(ip_address):
    with app.app_context():
        controller = Controller.query.filter_by(address=ip_address).first()
        if controller:
            return controller
        else:
            dummy_controller = Controller(
                address=ip_address,  # Dummy IP address
                controller_name=ip_address + " - No name",  # Dummy controller name
                id='999'  # Dummy controller name
            )
            return dummy_controller




def input_udp(data, addr):
    with app.app_context():
        message = inputs_pb2.inputCOV()  # replace with your protobuf message class
        message.ParseFromString(data)
        # dt_object = datetime.datetime.fromtimestamp(int(message.time_stamp) / 1000)
        # formatted_date = dt_object.strftime("%Y-%m-%d %H:%M:%S:%f")
        # print(formatted_date, end=' ')
        # print('input:', message.input, end=' ')
        # print('status:', inputs_pb2.OnChangeStatus.Name(message.status), end=' ')
        # ipaddress = addr[0]
        # controller = int(ipaddress.split('.')[-1])
        # print('from:', addr)


        ip = ''.join([str(element) for element in addr[0]])
        input_id = message.input  # Choose a random input id
        edge = inputs_pb2.OnChangeStatus.Name(message.status)  # Choose a random edge type
        controller = get_controller_by_ip(ip)

        name = ip +", "
        if controller:
            state = True
            if edge == "FALLING_EDGE":
                state = False
            input_key = f"{ip}_{input_id}"
            input_states[input_key] = (controller.id, input_id, state)
            socketio.emit('input_states', {'states': {input_key: input_states[input_key]}})
            # socketio.emit('inputs', {'controller': controller, 'input_id': input_id, 'OnChangeStatus': edge})
            name = f"{controller.controller_name}, "


        name = name.ljust(25)
        ip = f"Address: {ip}, ".ljust(25)
        input_id = f"Input: {input_id}, ".ljust(15)
        edge = f" {edge}, ".ljust(20)
        data = f"{name}{input_id}{edge}{ip}"
        latest_values.append(data)
        if len(latest_values) > 100:  # Only keep the last 100 values
            latest_values.pop(0)
        socketio.emit('input_value', {'data': data})

