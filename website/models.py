from . import db
from flask_login import UserMixin

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum('Admin', 'Manager', 'Worker'))

class Department(db.Model):
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Worker(db.Model, UserMixin):
    __tablename__ = 'workers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    status = db.Column(db.Enum('active', 'inactive'), default='active')

    department = db.relationship("Department", backref="workers")
    role = db.relationship("Role")

from sqlalchemy import Enum, TIMESTAMP, BOOLEAN

class TaskType(db.Model):
    __tablename__ = 'tasktype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('workers.id'))
    created_time = db.Column(TIMESTAMP, server_default=db.func.current_timestamp())
    status = db.Column(Enum('Not started', 'In progress', 'Completed', 'Frozen'))
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))
    completed_time = db.Column(TIMESTAMP)
    type_id = db.Column(db.Integer, db.ForeignKey('tasktype.id'))
    manager_id = db.Column(db.Integer, db.ForeignKey('workers.id'))
    text = db.Column(db.TEXT)

    created_by_worker = db.relationship("Worker", foreign_keys=[created_by])
    worker = db.relationship("Worker", foreign_keys=[worker_id])
    task_type = db.relationship("TaskType")
    manager = db.relationship("Worker", foreign_keys=[manager_id])

class TaskAssignment(db.Model):
    __tablename__ = 'taskassignment'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    previous_worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))
    new_worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))
    refused = db.Column(BOOLEAN, default=False)
    reassignment_time = db.Column(TIMESTAMP, server_default=db.func.current_timestamp())

    task = db.relationship("Task")
    previous_worker = db.relationship("Worker", foreign_keys=[previous_worker_id])
    new_worker = db.relationship("Worker", foreign_keys=[new_worker_id])

class TaskTypeWorker(db.Model):
    __tablename__ = 'tasktypeworker'

    id = db.Column(db.Integer, primary_key=True)
    tasktype_id = db.Column(db.Integer, db.ForeignKey('tasktype.id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))

    tasktype = db.relationship("TaskType")
    worker = db.relationship("Worker", foreign_keys=[worker_id])

class DeviceType(db.Model):
    __tablename__ = 'device_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class DeviceBrand(db.Model):
    __tablename__ = 'device_brand'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Device(db.Model):
    __tablename__ = 'Devices'

    device_id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(255))
    device_type_id = db.Column(db.Integer, db.ForeignKey('device_type.id'))
    device_brand_id = db.Column(db.Integer, db.ForeignKey('device_brand.id'))
    serial_number = db.Column(db.String(50), unique=True)

    status = db.Column(Enum('Available', 'Sent', 'Occupied', 'Returned', 'In repairs', 'Not available'), default='Available') 

    device_type = db.relationship("DeviceType")
    device_brand = db.relationship("DeviceBrand")

class DeviceWorker(db.Model):
    __tablename__ = 'device_worker'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('Devices.device_id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('workers.id'))
    request_id = db.Column(db.Integer, db.ForeignKey('device_request.id'))
    status = db.Column(db.Enum('Processing', 'In progress', 'Finished'))
    received_date = db.Column(db.TIMESTAMP)
    returned_date = db.Column(db.TIMESTAMP)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))

    device = db.relationship('Device', backref='device_workers')
    created_by = db.relationship('Worker', backref='created_device_workers', foreign_keys=[created_by_id])
    request = db.relationship('DeviceRequest', backref='device_workers')
    worker = db.relationship('Worker', backref='assigned_device_workers', foreign_keys=[worker_id])

class DeviceRequest(db.Model):
    __tablename__ = 'device_request'

    id = db.Column(db.Integer, primary_key=True)
    device_type_id = db.Column(db.Integer, db.ForeignKey('device_type.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('workers.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id')) 
    created_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    notes = db.Column(db.Text)

    device_type = db.relationship('DeviceType')
    created_by = db.relationship('Worker')
    task = db.relationship('Task') 

class DeviceReturnRequest(db.Model):
    __tablename__ = 'device_return_request'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device_type.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('workers.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id')) 
    notes = db.Column(db.Text)

    created_by = db.relationship('Worker')
    task = db.relationship('Task')

class RepairRequest(db.Model):
    __tablename__ = 'repair_request'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('Devices.device_id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('workers.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))

    device = db.relationship('Device')
    task = db.relationship('Task')
