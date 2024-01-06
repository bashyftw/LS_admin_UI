from flask import render_template, request, flash
from flask_login import login_required
from database import get_controller_name, Controller
from app import app, socketio

from grpc_functions import *

from routes.controllers import get_controller

MULTICAST_GROUP = '224.0.0.9'
audio_history = []
history_limit = 200


@socketio.on('audio_history_request')
def input_history_request():
    print("audio_history_request")
    for audio in audio_history:
        print(audio)
        socketio.emit('audio_history', audio)


@app.route('/audio', methods=['GET'])
@login_required
def audio():
    return render_template('audio/audio.html')


@app.route('/get_audio_stack_request/<int:controller_id>')
def get_audio_stack_request(controller_id):
    controller = get_controller(controller_id)
    print(controller_id)
    try:
        grpc_response = get_audio_stack(controller.address)


        testing = [
            {'file_name': 'MM_Bass.wav', 'speaker_output': [0, 1, 99, 99, 99, 99, 99, 99], 'start_time': 1704365374211,
             'end_time': 1704365377819, 'volume': 0.5},
            {'file_name': 'MM_Ba223ss.wav', 'speaker_output': [0, 1, 99, 99, 99, 99, 99, 99],
             'start_time': 1704365374211, 'end_time': 1704365377819, 'volume': 0.5}]

        return grpc_response

    except grpc.RpcError:
        pass

    except Exception as error:
        print(error)

    return []


@app.route('/remove_audio_file/<int:controller_id>/<string:file_name>/<int:start_time>')
def remove_audio_file(controller_id, file_name, start_time):
    controller = get_controller(controller_id)

    try:
        print(controller.address, file_name, start_time)
        grpc_response = remove_audio(controller.address, file_name, start_time)
        socketio.emit('audio_messages', {"type": grpc_response.success, "message": controller.address + " : " + grpc_response.message})

        return '', 200

    except grpc.RpcError:
        pass

    except Exception as e:
        # Handle the exception and return an error response
        print(e)
        return jsonify({'error': 'Operation failed', 'details': str(e)}), 500


@app.route('/remove_audio_controller/<int:controller_id>')
def remove_audio_controller(controller_id):
    controller = get_controller(controller_id)

    try:
        audio_files = get_audio_stack(controller.address, True)
        for audio_file in audio_files.audio_files:
            grpc_response = remove_audio_audiofile(controller.address, audio_file)
            socketio.emit('audio_messages', {"type": grpc_response.success, "message": controller.address + " : " + grpc_response.message})
        return '', 200

    except grpc.RpcError:
        pass

    except Exception as e:
        # Handle the exception and return an error response
        print(e)
        return jsonify({'error': 'Operation failed', 'details': str(e)}), 500


@app.route('/remove_audio_all', methods=['GET'])
def remove_audio_all():
    all_controllers = Controller.query.all()
    try:
        for controller in all_controllers:
            audio_files = get_audio_stack(controller.address, True)
            for audio_file in audio_files.audio_files:
                grpc_response = remove_audio_audiofile(controller.address, audio_file)
                socketio.emit('audio_messages', {"type": grpc_response.success, "message": controller.address + " : " + grpc_response.message})

        return '', 200

    except grpc.RpcError:
        pass

    except Exception as e:
        # Handle the exception and return an error response
        print(e)
        return jsonify({'error': 'Operation failed', 'details': str(e)}), 500

def audio_callback(data, addr):
    with app.app_context():
        audio_cov = parse_audio(data, addr)
        if audio_cov is None:
            print(data + addr)
            print("Failed to parse message.")
            return

        # Get controller name
        audio_cov_dict = audio_cov.to_dict()
        controller = get_controller_name(addr[0])
        audio_cov_dict['name'] = controller.name
        audio_cov_dict['id'] = controller.id
        print(audio_cov_dict)

        # Save history
        audio_history.append(audio_cov_dict)
        if len(audio_history) > history_limit:
            audio_history.pop(0)

        # Sent socket data
        socketio.emit('audio', audio_cov_dict)
