from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, IPAddress
from database import Controller
from app import app, db
from sqlalchemy.exc import IntegrityError

from grpc_stuff.grpc_functions import *
from routes.logs import log_event
import time

import grpc
import sys

sys.path.append('proto')
from grpc_stuff.proto import admin_pb2, admin_pb2_grpc

from enum import Enum


class ServiceEnum(str, Enum):
    led_server = 'led_server',
    audio_server = 'audio_server',
    input_server = 'input_server',
    admin_server = 'admin_server',
    file_server = 'file_server',
    web_server = 'web_server',
    go_control = 'go_control',
    chrony = 'chrony'


def get_controller(controller_id):
    controller = Controller.query.get(controller_id)
    if not controller:
        flash('Controller not found ', 'error')
        return redirect(url_for('controllers'))

    return controller


class ControllerForm(FlaskForm):
    controller_name = StringField('Controller name', validators=[DataRequired()])
    address = StringField("Ip address: ", validators=[DataRequired(), IPAddress(message="Invalid IP address!")])
    submit = SubmitField('Add/Edit Controller')


@app.route('/controllers', methods=['GET'])
@login_required
def controllers():
    page = request.args.get('page', 1, type=int)
    controllers = Controller.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('controllers/controllers.html', controllers=controllers, page=page)


@app.route('/add_controller', methods=['GET', 'POST'])
@login_required
def add_controller():
    form = ControllerForm()
    if form.validate_on_submit():
        print(form.address, form.controller_name)
        controller = Controller()
        controller.controller_name = form.controller_name.data
        controller.address = form.address.data
        db.session.add(controller)
        try:
            db.session.commit()
            log_event('Controller added: ' + controller.controller_name)
            flash('Controller added: ' + controller.controller_name, 'success')
            return redirect(url_for('controllers'))
        except IntegrityError as e:
            print(e)
            db.session.rollback()
            flash('Controller address already exists', 'error')
    return render_template('controllers/add_controller.html', form=form, form_title="Add Controller")


@app.route('/edit_controller/<int:controller_id>', methods=['GET', 'POST'])
@login_required
def edit_controller(controller_id):
    controller = get_controller(controller_id)
    form = ControllerForm(obj=controller)
    if form.submit.data and form.validate_on_submit():
        controller.controller_name = form.controller_name.data
        controller.address = form.address.data
        try:
            db.session.commit()
            log_event('Controller updated: ' + controller.controller_name)
            flash('Controller updated: ' + controller.controller_name, 'success')
            return redirect(url_for('controllers'))
        except IntegrityError as e:
            db.session.rollback()
            flash('Controller address already exists', 'error')
    return render_template('controllers/add_controller.html', form=form, form_title="Edit Controller")


@app.route('/service_operation/<int:controller_id>/<string:service_name>/<string:operation>', methods=['GET'])
def service_operation(controller_id, service_name, operation):
    print(controller_id, service_name, operation)

    controller = get_controller(controller_id)

    try:
        grpc_response = set_service_operation_gprc(
            controller.address, service_name, operation
        )
        print(grpc_response)
        return grpc_response

    except grpc.RpcError:
        pass

    except Exception as error:
        print(error)

    return False


@app.route('/get_services/<int:controller_id>', methods=['GET'])
def get_services(controller_id):
    controller = get_controller(controller_id)
    services = []
    try:
        for service in ServiceEnum:
            grpc_response = get_service(
                controller.address,
                service.name,
            )
            services.append(grpc_response)
            time.sleep(0.1)

        print(services)

    except grpc.RpcError:
        pass

    except Exception as error:
        print(error)

    return jsonify({"services": services})


@app.route('/get_controller_cpu/<int:controller_id>', methods=['GET'])
def get_controller_cpu(controller_id):
    controller = get_controller(controller_id)

    try:
        grpc_response = get_cpu(controller.address)
        return grpc_response

    except grpc.RpcError:
        pass

    except Exception as error:
        print(error)

    return False


@app.route('/details_controller/<int:controller_id>', methods=['GET', 'POST'])
@login_required
def details_controller(controller_id):
    controller = get_controller(controller_id)

    return render_template('controllers/details_controller.html', controller=controller)


@app.route('/delete_controller/<int:controller_id>', methods=['POST'])
@login_required
def delete_controller(controller_id):
    controller = get_controller(controller_id)
    db.session.delete(controller)
    db.session.commit()
    log_event('Controller deleted: ' + controller.controller_name)
    flash('Controller deleted: ' + controller.controller_name, 'success')
    return redirect(url_for('controllers'))


@app.route('/controller_status/<int:controller_id>')
def controller_status(controller_id):
    status = "Offline"
    controller = get_controller(controller_id)

    try:

        grpc_response = get_status(controller.address)
        status = grpc_response

    except grpc.RpcError:
        pass

    except Exception as error:
        print(error)

    return jsonify({'status': status})


@app.route('/reboot_controller/<int:controller_id>')
def reboot_controller(controller_id):
    controller = get_controller(controller_id)

    try:
        log_event('Controller rebooted: ' + controller.controller_name)

        reboot(controller.address)

    except grpc.RpcError:
        pass

    except Exception as error:
        print(error)

    return "reboot_controller"


@app.route('/get_files/<string:folder>/<int:controller_id>')
def get_files(folder, controller_id):
    controller = get_controller(controller_id)

    file_req = admin_pb2.fileReq()
    file_req.folder = folder

    try:
        with grpc.insecure_channel(controller.address + ':8888') as channel:
            stub = admin_pb2_grpc.adminServiceStub(channel)
            response = stub.GetFiles(file_req)
            print(response)

    except grpc.RpcError as e:
        return jsonify({'status': "Error"})
        print(e.code())
        print(e.details())

    return "get_files"
