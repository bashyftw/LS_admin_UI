import threading
import grpc
import sys
import datetime
import socket
import struct
import json
import os
import platform

from flask import jsonify

if platform.system() == 'Windows':
    proto_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../proto'))
    sys.path.append(proto_path)
else:  # Assuming Linux for all other cases
    sys.path.append('/home/pi/release/proto')

import inputs_pb2_grpc, inputs_pb2
import leds_pb2_grpc, leds_pb2
import audio_pb2_grpc, audio_pb2
import admin_pb2_grpc, admin_pb2
import server_pb2_grpc, server_pb2
import file_pb2_grpc, file_pb2

MULTICAST_GROUP = '224.0.0.9'  # replace with your multicast group
FILE_PORT = 4444
INPUT_PORT = 5555
LED_PORT = 6666
AUDIO_PORT = 7777
ADMIN_PORT = 8888
base_ip = '192.168.1.'


def is_full_ip(address):
    """Check if the given address is a full IP address."""
    parts = address.split('.')
    if len(parts) == 4 and all(part.isdigit() for part in parts):
        return address
    return base_ip + address


class InputCOV:
    def __init__(self, time_stamp, controller, input_id, status, adc):
        self.time_stamp = int(time_stamp)
        self.controller = controller
        self.input_id = input_id
        self.status = status
        self.adc = adc

    def __str__(self):
        if self.input_id < 70:
            return f"time_stamp: {format_timestamp(self.time_stamp)} " \
                   f" controller: {self.controller}" \
                   f" input: {self.input_id}" \
                   f" status: {self.status} "
        else:
            return f"time_stamp: {format_timestamp(self.time_stamp)} " \
                   f" controller: {self.controller}" \
                   f" input: {self.input_id}" \
                   f" adc: {self.adc} "

    def to_dict(self):
        if self.input_id < 70:
            return {
                "time_stamp": self.time_stamp,
                "controller": self.controller,
                "input": self.input_id,
                "status": self.status
            }
        else:
            return {
                "time_stamp": self.time_stamp,
                "controller": self.controller,
                "input": self.input_id,
                "adc": self.adc
            }


class AudioCOV:
    ADDED = audio_pb2.OnChangeStatus.Name(audio_pb2.OnChangeStatus.ADDED)
    STARTED = audio_pb2.OnChangeStatus.Name(audio_pb2.OnChangeStatus.STARTED)
    END_WARNING = audio_pb2.OnChangeStatus.Name(audio_pb2.OnChangeStatus.END_WARNING)
    REMOVED = audio_pb2.OnChangeStatus.Name(audio_pb2.OnChangeStatus.REMOVED)

    def __init__(self, time_stamp, start_time, end_time, controller, file_name, status, speaker_output):
        self.time_stamp = int(time_stamp)
        self.start_time = int(start_time)
        self.end_time = int(end_time)
        self.controller = controller
        self.file_name = file_name
        self.status = status
        self.speaker_output = speaker_output

    def __str__(self):
        return f"time_stamp: {format_timestamp(self.time_stamp)} " \
               f"controller: {self.controller} " \
               f"file_name: {self.file_name} " \
               f"status: {self.status} " \
               f"speaker_output: {self.speaker_output}" \
               f"start_time: {format_timestamp(self.start_time)} " \
               f"end_time: {format_timestamp(self.end_time)}"

    def to_dict(self):
        return {
            "time_stamp": self.time_stamp,
            "controller": self.controller,
            "file_name": self.file_name,
            "status": self.status,
            "speaker_output": self.speaker_output,
            "start_time": self.start_time,
            "end_time": self.end_time
        }


class LedCOV:
    ADDED = leds_pb2.OnChangeStatus.Name(leds_pb2.OnChangeStatus.ADDED)
    STARTED = leds_pb2.OnChangeStatus.Name(leds_pb2.OnChangeStatus.STARTED)
    END_WARNING = leds_pb2.OnChangeStatus.Name(leds_pb2.OnChangeStatus.END_WARNING)
    REMOVED = leds_pb2.OnChangeStatus.Name(leds_pb2.OnChangeStatus.REMOVED)

    def __init__(self, time_stamp, start_time, end_time, controller, file_name, status, universes):
        self.time_stamp = int(time_stamp)
        self.start_time = int(start_time)
        self.end_time = int(end_time)
        self.controller = controller
        self.file_name = file_name
        self.status = status
        self.universes = universes

    def __str__(self):
        return f"time_stamp: {format_timestamp(self.time_stamp)} " \
               f"controller: {self.controller} " \
               f"file_name: {self.file_name} " \
               f"status: {self.status} " \
               f"universes: {self.universes} " \
               f"start_time: {format_timestamp(self.start_time)} " \
               f"end_time: {format_timestamp(self.end_time)}"

    def to_dict(self):
        return {
            "time_stamp": self.time_stamp,
            "controller": self.controller,
            "file_name": self.file_name,
            "status": self.status,
            "universes": self.universes,
            "start_time": self.start_time,
            "end_time": self.end_time
        }


class ProcessStatus:
    def __init__(self, process, file_name, percentage, controller):
        self.process = process
        self.file_name = file_name
        self.percentage = percentage
        self.controller = controller

    def __str__(self):
        return f" controller: {self.controller}" \
               f" process: {self.process}" \
               f" file_name: {self.file_name}" \
               f" percentage: {self.percentage} "

    def to_dict(self):
        return {
            "controller": self.controller,
            "process": self.process,
            "file_name": self.file_name,
            "percentage": self.percentage,
        }


def parse_message(message, data):
    try:
        message.ParseFromString(data)
        return True
    except grpc.RpcError as e:
        print(f"{e.code()} {e.details()}")
        return False


def parse_file_process(data, addr):
    message = file_pb2.FileProcessStatus()
    if not parse_message(message, data):
        return None

    ipaddress = addr[0]
    controller = int(ipaddress.split('.')[-1])
    return ProcessStatus(message.process, message.file_name, round(message.percentage, 2), controller)


def parse_input(data, addr):
    message = inputs_pb2.inputCOV()
    if not parse_message(message, data):
        return None
    ipaddress = addr[0]
    controller = int(ipaddress.split('.')[-1])
    input_id = message.input - (controller * 100)
    status = inputs_pb2.OnChangeStatus.Name(message.status)
    adc = message.adc

    return InputCOV(message.time_stamp, controller, input_id, status, adc)


def parse_audio(data, addr):
    message = audio_pb2.AudioCOV()
    if not parse_message(message, data):
        return None

    ipaddress = addr[0]
    controller = int(ipaddress.split('.')[-1])
    status = audio_pb2.OnChangeStatus.Name(message.status)
    speakers = sorted(list(message.speakerOutput))

    return AudioCOV(message.time_stamp, message.start_time, message.end_time, controller,
                    message.fileName, status, speakers)


def parse_led(data, addr):
    message = leds_pb2.ledCOV()
    if not parse_message(message, data):
        return None

    ipaddress = addr[0]
    controller = int(ipaddress.split('.')[-1])
    status = leds_pb2.OnChangeStatus.Name(message.status)
    universes = sorted(list(message.universes))

    return AudioCOV(message.time_stamp, message.start_time, message.end_time, controller,
                    message.fileName, status, universes)


def format_timestamp(time_stamp):
    dt_object = datetime.datetime.fromtimestamp(int(time_stamp) / 1000)
    time_stamp_formatted = dt_object.strftime("%Y-%m-%d %H:%M:%S:%f")
    return time_stamp_formatted


def multicast_listener(port, callback):
    def listener(port, callback):
        # Create the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))

        # Tell the operating system to add the socket to the multicast group
        group = socket.inet_aton(MULTICAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            data, addr = sock.recvfrom(10240)
            callback(data, addr)

    # threading.Thread(target=listener, args=(port, callback)).start()
    thread = threading.Thread(target=listener, args=(port, callback))
    thread.daemon = True
    thread.start()


def addAudio(controller, time_stamp, file_name, output, volume):
    def addAudioMSG(controller, time_stamp, file_name, output, volume):
        address = is_full_ip(controller)
        try:
            # Create a gRPC channel and stub
            channel = grpc.insecure_channel(address + ':' + str(AUDIO_PORT))
            add_req = audio_pb2.AudioAddReq()
            add_req.start_time = time_stamp
            add_req.fileName = file_name
            add_req.speakerOutput.extend(output)
            add_req.volume = volume
            add_req.replace = False
            stub = audio_pb2_grpc.AudioServiceStub(channel)
            response = stub.AddAudio(add_req)

            # Print the response
            print(str(controller) + " Audio added : " + str(response.successful))

            # Close the channel
            channel.close()
        except grpc.RpcError as e:
            print(controller, end=' ')
            print(e.code(), end=' ')
            print(e.details(), end=' ')
            print(file_name)

    threading.Thread(target=addAudioMSG, args=(controller, time_stamp, file_name, output, volume)).start()


def add_led(controller, time_stamp, file_name):
    def add_led_msg(controller, time_stamp, file_name):
        address = is_full_ip(controller)
        try:
            # Create a gRPC channel and stub
            channel = grpc.insecure_channel(address + ':' + str(LED_PORT))
            add_req = leds_pb2.ledAddReq()
            add_req.start_time = time_stamp
            add_req.fileName = file_name
            add_req.replace = False
            stub = leds_pb2_grpc.LedsServiceStub(channel)
            response = stub.AddLed(add_req)

            # Print the response
            print(str(controller) + " LED added : " + str(response.successful) + " " + file_name)

            # Close the channel
            channel.close()
        except grpc.RpcError as e:
            print(controller, end=' ')
            print(e.code(), end=' ')
            print(e.details(), end=' ')
            print(file_name)

    threading.Thread(target=add_led_msg, args=(controller, time_stamp, file_name)).start()


def get_adc_value(controller):
    address = is_full_ip(controller)
    try:
        with grpc.insecure_channel(address + ':' + str(INPUT_PORT)) as channel:
            stub = inputs_pb2_grpc.InputsServiceStub(channel)

            adc_input_id = controller * 100 + 71
            input_adc = inputs_pb2.inputStateReq(input_id=adc_input_id)
            response = stub.GetState(input_adc)
            print(response.adc)
            return int(response.adc * 100)
    except grpc.RpcError as e:
        print(controller, end=' ')
        print(e.code(), end=' ')
        print(e.details())


def set_volume_all(volume, controllers):
    def add_volume_msg(volume, controller):
        try:
            with grpc.insecure_channel(controller) as channel:
                stub = admin_pb2_grpc.adminServiceStub(channel)

                vol = admin_pb2.volumeMSG(volume=volume)
                response2 = stub.SetAllChannelsVolume(vol)
                print("volume set " + str(response2.volume))

        except grpc.RpcError as e:
            print(controller, end=' ')
            print(e.code(), end=' ')
            print(e.details())

    for controller_number in controllers:
        address = is_full_ip(controller_number)
        controller = address + ':' + str(ADMIN_PORT)
        threading.Thread(target=add_volume_msg, args=(volume, controller)).start()


def set_service_operation_gprc(controller, service_name, operation):
    operation_map = {
        'start': admin_pb2.START,
        'stop': admin_pb2.STOP,
        'restart': admin_pb2.RESTART,
        'enable': admin_pb2.ENABLE,
        'disable': admin_pb2.DISABLE,
    }

    operation_req = admin_pb2.serviceOperationReq()
    operation_req.operation = operation_req.operation = operation_map.get(operation)
    operation_req.service = service_name

    address = is_full_ip(controller)

    try:
        with grpc.insecure_channel(address + ':' + str(ADMIN_PORT)) as channel:
            stub = admin_pb2_grpc.adminServiceStub(channel)

            response = stub.ServiceOperation(operation_req)

            service = {
                "name": response.service,
                "status": response.status,
                "enabled": response.enabled,
            }
            return service
    except grpc.RpcError as e:
        print(controller, end=' ')
        print(e.code(), end=' ')
        print(e.details())
        raise


def get_service(controller, service_name):
    service_req = admin_pb2.serviceReq()
    address = is_full_ip(controller)

    try:
        with grpc.insecure_channel(address + ':' + str(ADMIN_PORT)) as channel:
            stub = admin_pb2_grpc.adminServiceStub(channel)

            service_req.service = service_name
            response = stub.GetServiceDetails(service_req)
            service = {
                "name": response.service,
                "status": response.status,
                "enabled": response.enabled,
            }

            return service

    except grpc.RpcError as e:
        print(controller, end=' ')
        print(e.code(), end=' ')
        print(e.details())
        raise


def get_cpu(controller):
    empty_req = admin_pb2.empty()
    address = is_full_ip(controller)

    try:
        with grpc.insecure_channel(address + ':' + str(ADMIN_PORT)) as channel:
            stub = admin_pb2_grpc.adminServiceStub(channel)
            response = stub.GetCPUDetails(empty_req)
            cpu = {
                "CPU": list(response.CPU),
                "ram": response.ram,
                "harddrive": response.harddrive,
                "temp": response.temp,
                "throttled": response.throttled,
            }
            return jsonify(cpu)

    except grpc.RpcError as e:
        print(controller, end=' ')
        print(e.code(), end=' ')
        print(e.details())
        raise


def get_status(controller):
    server_req = server_pb2.ServerRequest()  # Create an instance of ServerRequest
    address = is_full_ip(controller)
    try:
        with grpc.insecure_channel(address + ':' + str(ADMIN_PORT)) as channel:
            stub = server_pb2_grpc.ServerServiceStub(channel)
            response = stub.GetStatus(server_req)
            return server_pb2.ServerStatus.Name(response.status)

    except grpc.RpcError as e:
        print(controller, end=' ')
        print(e.code(), end=' ')
        print(e.details())
        raise


def reboot(controller):
    empty_req = admin_pb2.empty()
    address = is_full_ip(controller)

    try:
        with grpc.insecure_channel(address + ':' + str(ADMIN_PORT)) as channel:
            stub = admin_pb2_grpc.adminServiceStub(channel)
            response = stub.RebootNow(empty_req)
            return True

    except grpc.RpcError as e:
        print(controller, end=' ')
        print(e.code(), end=' ')
        print(e.details())
        raise


def create_folder(controller, file_name):
    address = is_full_ip(controller)
    try:
        with grpc.insecure_channel(address + ':' + str(FILE_PORT)) as channel:
            stub = file_pb2_grpc.FilePackageStub(channel)

            # Create a FileOperationRequest
            request = file_pb2.FileOperationRequest(
                file_name=file_name,
                operation=file_pb2.FileOperation.CREATE
            )

            # Call the RunFileOperation RPC method
            response = stub.RunFileOperation(request)
            return response

    except grpc.RpcError as e:
        print(controller, end=' ')
        print(e.code(), end=' ')
        print(e.details())
        raise


def get_file_structure(controller, root_path, depth):
    address = is_full_ip(controller)
    try:
        with grpc.insecure_channel(address + ':' + str(FILE_PORT)) as channel:
            stub = file_pb2_grpc.FilePackageStub(channel)

            # Prepare the request
            request = file_pb2.FileStructureRequest(root_path=root_path, depth=depth)

            # Make the gRPC call
            response = stub.GetFileStructureAsJson(request)

            # Parse JSON response
            file_structure = json.loads(response.json_data)

            # Print or do something with the file_structure
            # print(json.dumps(file_structure, indent=4))

            return file_structure

    except grpc.RpcError as e:
        print(controller, end=' ')
        print(e.code(), end=' ')
        print(e.details())
        raise
