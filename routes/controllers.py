from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from flask_login.mixins import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, IPAddress
from werkzeug.security import generate_password_hash, check_password_hash
from database import Controller
from app import app, db
from sqlalchemy.exc import IntegrityError
from routes.logs import log_event
import random
import time

import grpc
import sys
sys.path.append('proto')
from proto import admin_pb2_grpc, admin_pb2
from proto import server_pb2_grpc, server_pb2

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
    return render_template('controllers/add_controller.html', form=form, form_title = "Add Controller")


from flask import jsonify, request, flash
from app import app, db
from database import Controller
from flask_login import login_required
from sqlalchemy.exc import IntegrityError


@app.route('/api/add_controller', methods=['POST'])
@login_required
def add_controller_api():
    """Add a new controller.

    Returns:
        JSON: Status of the operation.
    """
    data = request.get_json()
    if not data or 'address' not in data or 'controller_name' not in data:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    controller = Controller()
    controller.controller_name = data['controller_name']
    controller.address = data['address']
    db.session.add(controller)

    try:
        db.session.commit()
        log_event('Controller added: ' + controller.controller_name)
        return jsonify({"status": "success", "message": f"Controller added: {controller.controller_name}"})
    except IntegrityError as e:
        print(e)
        db.session.rollback()
        return jsonify({"status": "error", "message": "Controller address already exists"}), 400


@app.route('/edit_controller/<int:controller_id>', methods=['GET', 'POST'])
@login_required
def edit_controller(controller_id):
    controller = Controller.query.get(controller_id)
    if controller:
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
        return render_template('controllers/add_controller.html', form=form, form_title = "Edit Controller")
    flash('Controller not found', 'error')
    return redirect(url_for('controller'))

@app.route('/service_operation/<int:controller_id>/<string:service_name>/<string:operation>', methods=['GET'])
def service_operation(controller_id, service_name, operation):
    print(controller_id, service_name, operation)

    controller = Controller.query.get(controller_id)
    if controller is None:
        return jsonify({'status': 'Controller not found'}), 404

    operation_map = {
        'start': admin_pb2.START,
        'stop': admin_pb2.STOP,
        'restart': admin_pb2.RESTART,
        'enable': admin_pb2.ENABLE,
        'disable': admin_pb2.DISABLE,
    }

    # Create a serviceOperationReq object
    operation_req = admin_pb2.serviceOperationReq()
    operation_req.operation = operation_map[operation]
    operation_req.service = service_name

    try:
        # Connect to the gRPC server and call the ServiceOperation method
        with grpc.insecure_channel(controller.address +':8888') as channel:
            stub = admin_pb2_grpc.adminServiceStub(channel)
            response = stub.ServiceOperation(operation_req)
            service = {
                "name": response.service,
                "status": response.status,
                "enabled": response.enabled,
            }
            # print(service)
            return jsonify(service), 200

    except grpc.RpcError as e:
        print(e.code())
        print(e.details())
        return jsonify({'status': 'Failed to perform operation'}), 500




@app.route('/get_services/<int:controller_id>', methods=['GET'])
def get_services(controller_id):
    controller = Controller.query.get(controller_id)
    service_list_req = admin_pb2.serviceListReply()
    service_req = admin_pb2.serviceReq()

    services = []
    try:
        with grpc.insecure_channel(controller.address + ':8888') as channel:
            stub = admin_pb2_grpc.adminServiceStub(channel)
            response = stub.GetServiceList(service_list_req)

            for service_name in response.service:
                service_req.service = service_name
                response2 = stub.GetServiceDetails(service_req)
                service = {
                    "name": response2.service,
                    "status": response2.status,
                    "enabled": response2.enabled,
                }
                # print(response2.service)
                # print(response2.status)
                # print(response2.enabled)

                time.sleep(0.02)
                services.append(service)

            return jsonify({"services": services})

    except grpc.RpcError as e:
        print(e.code())
        print(e.details())



@app.route('/get_cpu/<int:controller_id>', methods=['GET'])
def get_cpu(controller_id):
    controller = Controller.query.get(controller_id)
    empty_req = admin_pb2.empty()


    try:
        with grpc.insecure_channel(controller.address + ':8888') as channel:
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
        print(e.code())
        print(e.details())
        return jsonify({"error": str(e.details())}), 500




@app.route('/details_controller/<int:controller_id>', methods=['GET', 'POST'])
@login_required
def details_controller(controller_id):
    controller = Controller.query.get(controller_id)
    if not controller:
        flash('Controller not found ', 'error')
        return redirect(url_for('controllers'))
    # services = get_services(controller)


    return render_template('controllers/details_controller.html', controller=controller)

@app.route('/delete_controller/<int:controller_id>', methods=['POST'])
@login_required
def delete_controller(controller_id):
    controller = Controller.query.get(controller_id)
    db.session.delete(controller)
    db.session.commit()
    log_event('Controller deleted: ' + controller.controller_name)
    flash('Controller deleted: ' + controller.controller_name, 'success')
    return redirect(url_for('controllers'))



@app.route('/controller_status/<int:controller_id>')
def controller_status(controller_id):
    controller = Controller.query.get(controller_id)
    server_req = server_pb2.ServerRequest()  # Create an instance of ServerRequest

    status = "Offline"
    try:
        with grpc.insecure_channel(controller.address + ':8888') as channel:
            stub = server_pb2_grpc.ServerServiceStub(channel)
            response = stub.GetStatus(server_req)
            status = server_pb2.ServerStatus.Name(response.status)

    except grpc.RpcError as e:
        return jsonify({'status': status})
        print(e.code())
        print(e.details())

    # Replace the line below with your logic to get the controller status


    return jsonify({'status': status})


@app.route('/reboot_controller/<int:controller_id>')
def reboot_controller(controller_id):

    controller = Controller.query.get(controller_id)
    empty_req = admin_pb2.empty()

    try:
        with grpc.insecure_channel(controller.address + ':8888') as channel:
            stub = admin_pb2_grpc.adminServiceStub(channel)
            response = stub.RebootNow(empty_req)
            return redirect(url_for('controllers'))

    except grpc.RpcError as e:
        return jsonify({'status': "Error"})
        print(e.code())
        print(e.details())

    return "reboot_controller"


@app.route('/get_files/<string:folder>/<int:controller_id>')
def get_files(folder, controller_id):

    controller = Controller.query.get(controller_id)
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

