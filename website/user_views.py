from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .role_dec import role_required
from .models import Task, Worker, TaskType, TaskTypeWorker, Device, DeviceWorker, Department, DeviceRequest, DeviceReturnRequest, DeviceBrand, DeviceType, RepairRequest
from . import db
import random
from datetime import datetime
from .status_utils import determine_task_type
from sqlalchemy import inspect
from sqlalchemy import asc, desc

user_views = Blueprint('user_views', __name__, template_folder='user')

@user_views.route('/dashboard', methods=['GET', 'POST'])
@login_required
@role_required([3]) #User
def user_dashboard():
    tasks = Task.query.join(Worker, Task.created_by == Worker.id) \
                .filter(Task.worker_id == current_user.id) \
                .order_by(desc(Task.id)) \
                .all()  
    tasktypes = TaskType.query.all()

    status_column = inspect(Task).columns.status
    statuses = status_column.type.enums
    
    return render_template("user/user_dashboard.html", user=current_user, tasks = tasks, tasktypes = tasktypes, statuses = statuses)

# MANAGE REQUESTS
@user_views.route('/new_request', methods=['GET', 'POST'])
@login_required
@role_required([3]) #User
def new_request():
    managers = Worker.query \
        .join(Department) \
        .filter(Worker.role_id == 2) \
        .filter(Department.id == current_user.department_id) \
        .filter(Worker.status == 'active') \
        .all()
    random_manager = random.choice(managers)

    if request.method == 'POST':
        new_request = request.form['newRequest']
        if not new_request.strip(): 
            return redirect(url_for('user_views.new_request'))
        else:

            task_type = determine_task_type(new_request)
            workers = TaskTypeWorker.query \
                .join(Worker) \
                .filter(Worker.role_id == 3) \
                .filter(TaskTypeWorker.tasktype_id == int(task_type)) \
                .filter(Worker.id != current_user.id) \
                .filter(Worker.status == 'active') \
                .all()

            if workers:       
                random_worker = random.choice(workers)

                task = Task(created_by=int(current_user.id), status="Not started", text = new_request, manager_id = random_manager.id, type_id = int(task_type), worker_id = random_worker.worker_id)
                db.session.add(task)
                db.session.commit()
                try:
                    db.session.commit()
                    flash('Your request was successfully sent.', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash('An error occurred while creating request info: {}'.format(str(e)), 'error')
            
                return redirect(url_for('user_views.user_requests'))

    return render_template("user/new_request.html", user=current_user)

@user_views.route('/user_requests', methods=['GET', 'POST'])
@login_required
@role_required([3]) #User
def user_requests():
    tasks = Task.query.join(Worker, Task.created_by == Worker.id) \
                .filter(Task.created_by == current_user.id) \
                .all()  
    status_column = inspect(Task).columns.status
    statuses = status_column.type.enums
    return render_template("user/user_requests.html", user=current_user, tasks = tasks, statuses=statuses)

@user_views.route('/delete_request/<int:task_id>', methods=['POST'])
@login_required
@role_required([3]) 
def delete_request(task_id):
    task = Task.query.get_or_404(task_id)
    device_request = DeviceRequest.query.filter(DeviceRequest.task_id == task_id).first()

    if task.status == 'Not started':
        if task.type_id == 5:
            device_request = DeviceRequest.query.filter(DeviceRequest.task_id == task_id).first()
        
            if device_request:
                db.session.delete(device_request)
                db.session.commit()
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully.', 'success')

    return redirect(url_for('user_views.user_requests'))

#MANAGE PROFILES

@user_views.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required([3]) 
def user_profile():
    if request.method == 'POST':
        new_phone = request.form['phone']
        new_email = request.form['email']

        if new_email and len(new_email) < 16:
            flash('Email must be greater than 15 characters.', 'error')
            if new_email != current_user.email:
                current_user.email = new_email 
        elif new_phone and not new_phone.isdigit():
            flash('Phone number should contain only numbers.', 'error')
            if new_phone != current_user.phone:
                        current_user.phone = new_phone

        db.session.commit()
        flash('Personal info changed successfully', 'success')
        return redirect(url_for('user_views.user_profile'))
     
    return render_template("user/user_profile.html", user=current_user)


@user_views.route('/user_profile/<user_id>', methods=['GET', 'POST'])
@login_required
@role_required([3]) 
def view_profile(user_id):
    user = Worker.query \
                .join(Department) \
                .filter(Worker.id == user_id) \
                .first()
     
    return render_template("user/view_profile.html", user=user)

#REVIEW TASKS

@user_views.route('/review_request/<task_id>', methods=['GET', 'POST'])
@login_required
@role_required([3]) 
def review_request(task_id):
    task = Task.query.get_or_404(task_id)
    task_type = TaskType.query.get_or_404(task.type_id).name
    status_column = inspect(Task).columns.status
    statuses = status_column.type.enums
    

    if task_type == 'Device issue':
        return redirect(url_for('user_views.review_device_request', task_id=task_id))
    
    if task_type == 'Device return':
        return redirect(url_for('user_views.return_device_request', task_id=task_id))
    
    if request.method == 'POST':
        new_status = request.form.get('status')
        task_type = TaskType.query.get_or_404(task.type_id).name

        if new_status and new_status in ['Not started', 'In progress', 'Completed', 'Frozen']:
            if new_status == 'Completed' and not task.completed_time:
                    task.completed_time = datetime.now()              
            elif new_status != 'Completed':
                task.completed_time = None
            task.status = new_status
            db.session.commit()
            return redirect(url_for('user_views.review_request', task_id=task_id))


    return render_template("user/review_request.html", task=task, statuses=statuses)

@user_views.route('/reassign_request/<task_id>', methods=['GET', 'POST'])
@login_required
@role_required([3]) 
def reassign_request(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        workers = TaskTypeWorker.query \
                .join(Worker) \
                .filter(Worker.role_id == 3) \
                .filter(TaskTypeWorker.tasktype_id == int(task.task_type)) \
                .filter(Worker.id != current_user.id) \
                .filter(Worker.status == 'active') \
                .all()

        if workers:       
            random_worker = random.choice(workers)

        task.worker_id = random_worker
        task.status = 'Not started'
        db.session.commit()
        flash("You reassigned task id: {}".format(str(task_id)), 'success')
        return redirect(url_for('user_views.user_dashboard'))

    return render_template("user/user_dashboard.html", task=task)

#MANAGE DEVICES (USER)

@user_views.route('/user_devices', methods=['GET', 'POST'])
@login_required
@role_required([3])
def user_devices():
    user_devices = DeviceWorker.query \
        .join(DeviceRequest, DeviceWorker.request_id == DeviceRequest.id) \
        .join(Device, DeviceWorker.device_id == Device.device_id) \
        .join(DeviceBrand, Device.device_brand_id == DeviceBrand.id) \
        .join(DeviceType, Device.device_type_id == DeviceType.id) \
        .filter(DeviceWorker.created_by_id == current_user.id) \
        .all()
    
    devicetypes = DeviceType.query.all()
    devicebrands = DeviceBrand.query.all()
    status_column = inspect(DeviceWorker).columns.status
    statuses = status_column.type.enums

    for user_device in user_devices:
        print(user_device.device.device_name)
        print(user_device.status)

    
    return render_template("user/user_devices.html", user=current_user, user_devices = user_devices, devicetypes=devicetypes, devicebrands=devicebrands, statuses=statuses)

@user_views.route('/request_new_device', methods=['GET', 'POST'])
@login_required
@role_required([3])
def request_new_device():
    device_types = DeviceType.query.all()

    managers = Worker.query \
        .join(Department) \
        .filter(Worker.role_id == 2) \
        .filter(Department.id == current_user.department_id) \
        .filter(Worker.status == 'active') \
        .all()
    random_manager = random.choice(managers)

    workers = TaskTypeWorker.query \
        .join(Worker) \
        .filter(Worker.role_id == 3) \
        .filter(TaskTypeWorker.tasktype_id == 5) \
        .filter(Worker.id != current_user.id) \
        .filter(Worker.status == 'active') \
        .all()
    
    random_worker = random.choice(workers)

    
    if request.method == 'POST':
        device_id = request.form['device_type']
        notes = request.form['additional_notes']

        device = DeviceType.query.get_or_404(device_id)
        device_name = device.name

        task_text = f"New device request. Type: {device_name}. Notes: {notes}"

        task = Task(created_by=current_user.id, status="Not started", text=task_text, manager_id=random_manager.id, type_id = 5, worker_id = random_worker.worker_id)
        db.session.add(task)
        db.session.commit()

        # Create and add a new DeviceRequest instance
        device_request = DeviceRequest(created_by_id=int(current_user.id), created_date=datetime.now(), device_type_id=int(device_id), notes=notes, task_id=task.id)
        db.session.add(device_request)

        db.session.commit()
        flash('You created a new device request.', 'success')
        return redirect(url_for('user_views.user_requests'))
    
    return render_template("user/request_new_device.html", user=current_user, device_types=device_types)



@user_views.route('/confirm_device/<int:device_id>', methods=['POST'])
@login_required
@role_required([3])
def confirm_device(device_id):
    device = Device.query.get_or_404(device_id)
    device_worker = DeviceWorker.query.filter(DeviceWorker.device_id == device_id).filter(DeviceWorker.created_by_id == current_user.id).first_or_404()
    dv_task = DeviceWorker.query \
        .join(DeviceRequest, DeviceWorker.request_id == DeviceRequest.id) \
        .with_entities(DeviceRequest.task_id) \
        .first()
    task = Task.query.filter(Task.id == dv_task.task_id).first()

    device.status = 'Occupied'
    device_worker.status = 'In progress'
    device_worker.received_date = datetime.now()
    task.status = 'Completed'
    task.completed_time = datetime.now()
    
    db.session.commit()

    return redirect(url_for('user_views.user_devices', user=current_user))


@user_views.route('/return_device/<int:device_id>', methods=['GET', 'POST'])
@login_required
@role_required([3])
def return_device(device_id):
    managers = Worker.query \
        .join(Department) \
        .filter(Worker.role_id == 2) \
        .filter(Department.id == current_user.department_id) \
        .filter(Worker.status == 'active') \
        .all()
    random_manager = random.choice(managers)

    workers = TaskTypeWorker.query \
        .join(Worker) \
        .filter(Worker.role_id == 3) \
        .filter(TaskTypeWorker.tasktype_id == 6) \
        .filter(Worker.id != current_user.id) \
        .filter(Worker.status == 'active') \
        .all()
    
    random_worker = random.choice(workers)

    device_worker = DeviceWorker.query.filter(DeviceWorker.device_id == device_id).filter(DeviceWorker.created_by_id == current_user.id).first_or_404()

    if request.method == 'POST':
        device = Device.query.get_or_404(device_id)
        device.status = 'Returned'

        device_worker.status = 'Finished'
        device_worker.returned_date = datetime.now() 

        task_text = f"Return device. Name: {device.device_name}. Serial number: {device.serial_number}"

        task = Task(created_by = current_user.id, created_time = datetime.now(), status='Not started', type_id = 6, manager_id = random_manager.id, text = task_text, worker_id = random_worker.worker_id)
        db.session.add(task)
        db.session.commit()

        device_return_request = DeviceReturnRequest(created_by_id=int(current_user.id), device_id=device.device_id, notes=task_text, task_id=task.id)
        db.session.add(device_return_request)
       
        db.session.commit()

        return redirect(url_for('user_views.user_devices'))


    return render_template("user/user_devices.html", user=current_user)



# MANAGE DEVICES (WORKER)
@user_views.route('/review_device_request/<task_id>', methods=['GET', 'POST'])
@login_required
@role_required([3]) 
def review_device_request(task_id):
    task = Task.query.get_or_404(task_id)
    status_column = inspect(Task).columns.status
    statuses = status_column.type.enums
    device_request = DeviceRequest.query.filter(DeviceRequest.task_id == task.id).first()
    # WORK IN PROGRESS
    print(device_request)
    avail_devices = Device.query.filter(Device.device_type_id == device_request.device_type_id).filter(Device.status == 'Available').all()


    if request.method == 'POST':
        device_id = request.form['device']
        device = Device.query.get_or_404(device_id)

        device.status = 'Sent'
        device_request.status = 'Processing'
        task.status = 'In progress'

        new_deviceworker = DeviceWorker(device_id=device_id, created_by_id=device_request.created_by_id, request_id=device_request.id, status='Processing', worker_id=current_user.id)
        db.session.add(new_deviceworker)
        db.session.commit()
        return redirect(url_for('user_views.user_dashboard', task_id=task_id))
        

    return render_template("user/review_device_request.html", user=current_user, task=task, devices=avail_devices, statuses=statuses)

@user_views.route('/return_device_request/<task_id>', methods=['GET', 'POST'])
@login_required
@role_required([3]) 
def return_device_request(task_id):
    task = Task.query.get_or_404(task_id)
    status_column = inspect(Task).columns.status
    statuses = status_column.type.enums
    

    device_request = DeviceReturnRequest.query \
        .join(Task, Task.id == DeviceReturnRequest.task_id) \
        .filter(Task.id == task_id) \
        .first()


    device = Device.query.get_or_404(device_request.device_id)

    workers = TaskTypeWorker.query \
        .join(Worker) \
        .filter(Worker.role_id == 3) \
        .filter(TaskTypeWorker.tasktype_id == 7) \
        .filter(Worker.id != current_user.id) \
        .filter(Worker.status == 'active') \
        .all()
    
    random_worker = random.choice(workers)

    managers = Worker.query \
        .join(Department) \
        .filter(Worker.role_id == 2) \
        .filter(Department.id == current_user.department_id) \
        .filter(Worker.status == 'active') \
        .all()
    random_manager = random.choice(managers)

    user_devices = DeviceWorker.query \
        .filter(DeviceWorker.device_id == device_request.device_id) \
        .first()
    print(user_devices)

    if request.method == 'POST':
        device_status = request.form['deviceStatus']
        notes = request.form['repairNotes']

        task.status = 'Completed'
        task.completed_time = datetime.now()
        user_devices.returned_date = datetime.now()
        user_devices.status = 'Finished'

        db.session.commit()

        if device_status == 'In repairs':

            task_text = f"Repair device. Name: {device.device_name}. Serial number: {device.serial_number} Notes: {notes}"

            task = Task(created_by = current_user.id, created_time = datetime.now(), status='Not started', type_id = 7, manager_id = random_manager.id, text = task_text, worker_id = random_worker.worker_id)
            db.session.add(task)
            db.session.commit()

            repair_request =  RepairRequest(created_by_id=int(current_user.id), device_id=device.device_id, task_id=task.id)
            db.session.add(repair_request)
            db.session.commit()
        else:
            device.status = 'Available'

        db.session.commit()
        return redirect(url_for('user_views.user_dashboard', task_id=task_id))
        

    return render_template("user/return_device_request.html", user=current_user, task=task, device=device, statuses = statuses)



@user_views.route('/questions', methods=['GET', 'POST'])
@login_required
@role_required([3])
def questions():
    return render_template("user/questions.html")