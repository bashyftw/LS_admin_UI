from app import app, socketio
import threading
import socket
import struct
import sys
# from routes.inputs import get_controller_by_ip

sys.path.append('../grpc_stuff/proto')
from grpc_stuff.proto import audio_pb2, inputs_pb2, leds_pb2

MULTICAST_GROUP = '224.0.0.9'
input_data = []
led_data = []
audio_data = []
history_limit = 200


# def multicast_listener(port, callback):
#     def listener(port, callback):
#         # Create the socket
#         sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         sock.bind(('', port))
#
#         # Tell the operating system to add the socket to the multicast group
#         group = socket.inet_aton(MULTICAST_GROUP)
#         mreq = struct.pack('4sL', group, socket.INADDR_ANY)
#         sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
#
#         while True:
#             data, addr = sock.recvfrom(10240)
#             callback(data, addr)
#
#     # threading.Thread(target=listener, args=(port, callback)).start()
#     thread = threading.Thread(target=listener, args=(port, callback))
#     thread.daemon = True
#     thread.start()


# def input_udp2(data, addr):
#     with app.app_context():
#         message = inputs_pb2.inputCOV()
#         message.ParseFromString(data)
#
#         ip = ''.join([str(element) for element in addr[0]])
#         controller = get_controller_by_ip(ip)
#
#         input_id = message.input  # Choose a random input id
#         status = inputs_pb2.OnChangeStatus.Name(message.status)
#         # dt_object = datetime.datetime.fromtimestamp(int(message.time_stamp) / 1000)
#         # timestamp = dt_object.strftime("%Y-%m-%d %H:%M:%S:%f")
#
#         input = {'ip': ip, 'input_id': input_id, 'status': status, 'timestamp': message.time_stamp,
#                  'controller_id': controller.id, 'controller_name': controller.controller_name}
#         # print(input)
#
#         input_data.append(input)
#         if len(input_data) > history_limit:  # Only keep the last 100 values
#             input_data.pop(0)
#         socketio.emit('input_data', {'input': input})


def led_udp(data, addr):
    with app.app_context():
        message = leds_pb2.ledCOV()
        message.ParseFromString(data)

        ip = ''.join([str(element) for element in addr[0]])
        controller = get_controller_by_ip(ip)

        status = leds_pb2.OnChangeStatus.Name(message.status)

        universes = sorted(list(message.universes))
        led = {'ip': ip, 'file_name': message.fileName, 'status': status, 'start_time': message.start_time,
               'end_time': message.end_time, 'universes': universes, 'controller_id': controller.id,
               'controller_name': controller.name, 'timestamp': message.time_stamp}

        led_data.append(led)
        if len(led_data) > history_limit:  # Only keep the last 100 values
            led_data.pop(0)
        socketio.emit('led_data', {'led': led})


def audio_udp(data, addr):
    with app.app_context():
        message = audio_pb2.AudioCOV()
        message.ParseFromString(data)

        ip = ''.join([str(element) for element in addr[0]])
        controller = get_controller_by_ip(ip)

        file_name = message.fileName
        status = audio_pb2.OnChangeStatus.Name(message.status)

        speakers = sorted(list(message.speakerOutput))
        # speakers = [1, 2, 3]
        audio = {'ip': ip, 'file_name': file_name, 'status': status, 'start_time': message.start_time,
                 'end_time': message.end_time, 'speakers': speakers, 'controller_id': controller.id,
                 'controller_name': controller.name, 'timestamp': message.time_stamp}

        audio_data.append(audio)
        if len(audio_data) > history_limit:
            audio_data.pop(0)
        socketio.emit('audio_data', {'audio': audio})


@socketio.on('input_history2')
def input_history2():
    for input in input_data:
        socketio.emit('input_data', {'input': input})


@socketio.on('led_history')
def led_history():
    for led in led_data:
        socketio.emit('led_data', {'led': led})


@socketio.on('audio_history')
def audio_history():
    for audio in audio_data:
        socketio.emit('audio_data', {'audio': audio})


@socketio.on('connect')
def connect():
    print('Socket connection')
