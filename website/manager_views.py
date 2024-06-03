from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .role_dec import role_required
from .models import Worker, Department, Role, Task, TaskType, TaskTypeWorker, DeviceBrand, DeviceType, Device, DeviceWorker
from . import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect, asc, desc

manager_views = Blueprint('manager_views', __name__, template_folder='manager')

@manager_views.route('/dashboard', methods=['GET', 'POST'])
@login_required
@role_required([2]) #Manager
def manager_dashboard():

    tasks = Task.query \
            .join(Worker, Task.created_by == Worker.id) \
            .outerjoin(TaskType) \
            .order_by(desc(Task.id)) \
            .all()
    tasktypes = TaskType.query.all()

    status_column = inspect(Task).columns.status
    statuses = status_column.type.enums
    return render_template("manager/manager_dashboard.html", user=current_user, tasks = tasks, tasktypes = tasktypes, statuses = statuses)

@manager_views.route('/edit_request/<int:task_id>', methods=['GET', 'POST'])
@login_required
@role_required([2]) # Manager
def edit_request(task_id):
    task = Task.query.get_or_404(task_id)
    workers = Worker.query \
        .join(Role, Worker.role_id == Role.id) \
        .join(TaskTypeWorker, TaskTypeWorker.worker_id == Worker.id)\
        .filter(Worker.department_id == current_user.department_id) \
        .filter(Role.name == 'Worker')\
        .filter(Worker.id != task.created_by)\
        .filter(Worker.status == 'active') \
        .filter(TaskTypeWorker.tasktype_id == task.task_type.id) \
        .all()
    
    tasktypes = TaskType.query.all()
    if request.method == 'POST':
        new_worker_id = request.form['worker']
        new_type = request.form['taskType']

        if new_worker_id != task.worker_id:
            task.worker_id = new_worker_id
        if new_type != task.type_id:
            task.type_id = new_type

        db.session.commit()
        flash('Task edited successfully.', 'success') 
        return redirect(url_for('manager_views.manager_dashboard'))

    return render_template("manager/edit_request.html", task=task, workers=workers, tasktypes=tasktypes)

@manager_views.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required([2]) 
def manager_profile():
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
        return redirect(url_for('manager_views.manager_profile'))
     
    return render_template("manager/manager_profile.html", user=current_user)


@manager_views.route('/edit_profile/<user_id>', methods=['GET', 'POST'])
@login_required
@role_required([2]) 
def edit_profile(user_id):
    user = Worker.query.get_or_404(user_id)
   
    tasktypes = TaskType.query.all()
    worker_tasktypes = TaskTypeWorker.query.filter(TaskTypeWorker.worker_id == user_id).all()
    worker_tasktype_ids = [tasktype.tasktype_id for tasktype in worker_tasktypes]

    if request.method == 'POST':
        selected_tasktypes = set()
        for tasktype_id in request.form.getlist('tasktypes[]'):
            selected_tasktypes.add(int(tasktype_id))

        for tasktype_id in selected_tasktypes - set(worker_tasktype_ids):
            new_tasktype_worker = TaskTypeWorker(worker_id=user_id, tasktype_id=tasktype_id)
            db.session.add(new_tasktype_worker)

        for tasktype_id in set(worker_tasktype_ids) - selected_tasktypes:
            TaskTypeWorker.query.filter_by(worker_id=user_id, tasktype_id=tasktype_id).delete()

        try:
            db.session.commit()
            flash('User #{} was successfully disactivated.'.format(str(user_id)), 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating user info: {}'.format(str(e)), 'error')
        

        return redirect(url_for('manager_views.edit_profile', user_id=user.id))

    return render_template("manager/edit_profile.html", user=user, tasktypes=tasktypes, worker_tasktype_ids=worker_tasktype_ids, worker_tasktypes=worker_tasktypes)


@manager_views.route('/user_profile/<user_id>', methods=['GET', 'POST'])
@login_required
@role_required([2]) 
def view_profile(user_id):
    user = Worker.query.get_or_404(user_id)
   
    tasktypes = TaskType.query.all()
    worker_tasktypes = TaskTypeWorker.query.filter(TaskTypeWorker.worker_id == user_id).all()
    worker_tasktype_ids = [tasktype.tasktype_id for tasktype in worker_tasktypes]

    return render_template("manager/view_profile.html", user=user, tasktypes=tasktypes, worker_tasktype_ids=worker_tasktype_ids, worker_tasktypes=worker_tasktypes)


@manager_views.route('/manage_devices', methods=['GET', 'POST'])
@login_required
@role_required([2]) #Manager
def manage_devices():
    device_workers = DeviceWorker.query \
        .join(Device, DeviceWorker.device_id == Device.device_id) \
        .join(DeviceBrand, Device.device_brand_id == DeviceBrand.id) \
        .join(DeviceType, Device.device_type_id == DeviceType.id) \
        .order_by(asc(DeviceWorker.id)) \
        .all()
    

    devicetypes = DeviceType.query.all()
    devicebrands = DeviceBrand.query.all()

    status_column = inspect(DeviceWorker).columns.status
    statuses = status_column.type.enums
    return render_template("manager/manage_devices.html", user=current_user, device_workers=device_workers, statuses=statuses, devicetypes=devicetypes, devicebrands=devicebrands )


@manager_views.route('/add_new_device', methods=['GET', 'POST'])
@login_required
@role_required([2]) #Manager
def add_new_device():

    devices = DeviceWorker.query.join(Device).join(DeviceBrand).join(DeviceType).all()
    device_types = DeviceType.query.all()
    device_brands = DeviceBrand.query.all()
    if request.method == 'POST':
        device_name = request.form['device_name']
        device_type = request.form['device_type']
        device_brand = request.form['device_brand']
        serial_number = request.form['serial_number']

        try: 
            new_device = Device(device_name = device_name, device_type_id = device_type, device_brand_id = device_brand, serial_number=serial_number)
            db.session.add(new_device)
            db.session.commit()
            flash('Device was successfully added', 'success')
            return redirect(url_for('manager_views.view_devices_list', user_id=current_user.id))
        except IntegrityError as e:
            flash('Serial number already exists. Please choose a different serial number.', 'error')
            return redirect(url_for('manager_views.add_new_device'))


    return render_template("manager/add_new_device.html", user=current_user, devices=devices, device_types=device_types, device_brands=device_brands)

@manager_views.route('/view_devices_list', methods=['GET', 'POST'])
@login_required
@role_required([2]) #Manager
def view_devices_list():
    device_list = Device.query \
        .join(DeviceBrand, Device.device_brand_id == DeviceBrand.id) \
        .join(DeviceType, Device.device_type_id == DeviceType.id) \
        .order_by(asc(Device.device_id)) \
        .all()
    
    devicetypes = DeviceType.query.all()
    devicebrands = DeviceBrand.query.all()
    status_column = inspect(Device).columns.status
    statuses = status_column.type.enums

    return render_template("manager/view_devices_list.html", device_list=device_list, devicetypes=devicetypes, devicebrands=devicebrands, statuses=statuses)


@manager_views.route('/make_not_available/<int:device_id>', methods=['POST'])
@login_required
@role_required([2]) 
def make_not_available(device_id):
    device = Device.query.get_or_404(device_id)

    device.status = '6'
    db.session.commit()
    flash('Device #{} is now not available.'.format(str(device_id)), 'success')
    return redirect(url_for('manager_views.view_devices_list'))


@manager_views.route('/manage_workers', methods=['GET', 'POST'])
@login_required
@role_required([2]) #Manager
def manage_workers():
    users = db.session.query(Worker, Department.name, Role.name).join(Department).join(Role) \
        .filter(Role.name == 'Worker').filter(Worker.department_id == current_user.department_id).filter(Worker.status == 'active').all()
    roles = Role.query.all()
    departments = Department.query.all()
    responsibilities = TaskTypeWorker.query.join(TaskType).all()

    tasktypes = TaskType.query.all()
    return render_template("manager/manage_workers.html", users = users, roles=roles, departments=departments, responsibilities = responsibilities, tasktypes=tasktypes)


@manager_views.route('/questions', methods=['GET', 'POST'])
@login_required
@role_required([2])
def questions():
    return render_template("manager/questions.html")


