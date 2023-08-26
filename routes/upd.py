from flask import Flask, render_template


import socket
from flask_socketio import emit
from app import app, socketio


import time
import random

latest_values = []
input_states = {}

# @app.route('/udp')
# def udp():
#     return render_template('udp.html')
#
# @socketio.on('connect')
# def handle_connect():
#     print('Client connected')
#
# @socketio.on('get_history')
# def handle_history():
#     for value in latest_values:
#         emit('new_value', {'data': value})
#
#
# def handle_udp():
#     while True:
#         time.sleep(random.randint(1, 5))  # Pause for a random interval between 1 and 5 seconds
#         data = "{} {} {}".format(
#             "192.168.1.{}".format(random.randint(1, 3)),  # Generate a random IP
#             random.choice(["input1", "input2", "input3"]),  # Choose a random input id
#             random.choice(["rising", "falling"])  # Choose a random edge type
#         )
#         ip, input_id, edge = data.split()  # Split the data into its three parts
#         state = True
#         if edge == "falling":
#             state = False
#         input_key = f"{ip}_{input_id}"
#         input_states[input_key] = state  # Store the last state of the input id
#         latest_values.append(data)
#         if len(latest_values) > 100:  # Only keep the last 100 values
#             latest_values.pop(0)
#         socketio.emit('new_value', {'data': data, 'states': input_states})  # Send the data and current states