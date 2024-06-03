from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .role_dec import role_required
from .models import Worker, Department, Role, Device, DeviceWorker, Task, TaskTypeWorker
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import asc, desc

admin_views = Blueprint('admin_views', __name__, template_folder='admin')

#====================== ADMIN =====================================
# View list of all workers
@admin_views.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
@role_required([1]) #Admin
def admin_dashboard():
    users = db.session.query(Worker, Department.name, Role.name).join(Department).join(Role).order_by(asc(Worker.id)).all()
    roles = Role.query.all()
    departments = Department.query.all()
    return render_template("admin/admin_dashboard.html", users = users, roles=roles, departments=departments)

# create a new user
@admin_views.route('/create_user', methods=['GET', 'POST'])
@login_required
@role_required([1]) #Admin
def create_user():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        phone = request.form['phone']
        title = request.form['title']
        department_id = request.form['department']
        role_id = request.form['role']
        username = request.form['username']
        password = request.form['password1']

        if len(email) < 16:
            flash('Email must be greater than 15 characters.', 'error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', 'error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', 'error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', 'error')
        else:
            user = Worker.query.filter_by(email=email).first()
            if user:
                flash('This user already exists.', 'error')
            else:
                new_user = Worker(first_name=first_name, last_name=last_name, email=email, phone=phone, 
                                  title=title, department_id=department_id, role_id=role_id,
                                  username=username, password_hash=generate_password_hash(password, method='pbkdf2:sha256'))
                db.session.add(new_user)
                db.session.commit()
                flash('User created successfully.', 'success')
                return redirect(url_for('admin_views.admin_dashboard'))
    
    roles = Role.query.all()
    departments = Department.query.all()
    return render_template("admin/create_user.html", user=current_user, departments=departments, roles=roles)


# disable user
@admin_views.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@role_required([1]) # Admin
def delete_user(user_id):
    user = Worker.query.get_or_404(user_id)
    user.status = 'inactive'

    #find all devices from this user and make them available
    devices = Device.query.join(DeviceWorker).filter(DeviceWorker.worker_id == user_id).all()
    for device in devices:
        device.status = 'Available'
    
    #delete all requests by this user that are not completed
    Task.query.filter(Task.created_by == user_id, Task.status != 'Completed').delete(synchronize_session=False)

    #delete all tasktype worker connections for this worker
    TaskTypeWorker.query.filter_by(worker_id=user_id).delete()

    #delete all device worker connections for this worker
    DeviceWorker.query.filter_by(worker_id=user_id).delete()


    try:
        db.session.commit()
        flash('User #{} was successfully disactivated.'.format(str(user_id)), 'success')
    except Exception as e:
        db.session.rollback()
        print('An error occurred while deleting tasks: {}'.format(str(e)))

    return redirect(url_for('admin_views.admin_dashboard'))


#update user information
@admin_views.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required([1])  # Admin
def edit_user(user_id):
    user = Worker.query.get_or_404(user_id)
    roles = Role.query.all()
    departments = Department.query.all()

    if request.method == 'POST':
        new_first_name = request.form['firstName']
        new_last_name = request.form['lastName']
        new_email = request.form['email']
        new_phone = request.form['phone']
        new_title = request.form['title']
        new_department_id = request.form['department']
        new_role_id = request.form['role']
        new_username = request.form['username']
        new_password = request.form['password']

        if len(new_email) < 16:
            flash('Email must be greater than 15 characters.', 'error')
        elif len(new_first_name) < 2:
            flash('First name must be greater than 1 character.', 'error')
        elif len(new_last_name) < 2:
            flash('Last name must be greater than 1 character.', 'error')
        elif new_password and len(new_password) < 7:
            flash('Password must be at least 7 characters.', 'error')
        else:
            email_user = Worker.query.filter_by(email=new_email).first()
            if email_user and email_user.id != user.id:
                flash('This email is already used by another user.', 'error')
            else:
                if new_first_name != user.first_name:
                    user.first_name = new_first_name
                if new_last_name != user.last_name:
                    user.last_name = new_last_name
                if new_email != user.email:
                    user.email = new_email
                if new_phone != user.phone:
                    user.phone = new_phone
                if new_title != user.title:
                    user.title = new_title
                if new_department_id != user.department_id:
                    user.department_id = new_department_id
                if new_role_id != user.role_id:
                    user.role_id = new_role_id
                if new_username != user.username:
                    user.username = new_username
                
                if new_password:
                    password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
                    user.password_hash = password_hash

                db.session.commit()
                flash('User edited successfully.', 'success')
                return redirect(url_for('admin_views.admin_dashboard'))

    return render_template("admin/edit_user.html", user=user, departments=departments, roles=roles)
