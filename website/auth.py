from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, logout_user, login_user
from werkzeug.security import check_password_hash
from .models import Worker

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Worker.query.filter_by(username=username).first()

        if user:
            if user.status == 'active':
                if check_password_hash(user.password_hash, password):
                    if user.role_id == 1:
                        # Admin
                        print("ADMIN")
                        login_user(user, remember=True)
                        return redirect(url_for('admin_views.admin_dashboard'))
                    elif user.role_id == 2:
                        # Manager
                        print("MANAGER")
                        login_user(user, remember=True)
                        return redirect(url_for('manager_views.manager_dashboard'))
                    elif user.role_id == 3:
                        # Worker
                        print("WORKER")
                        login_user(user, remember=True)
                        return redirect(url_for('user_views.user_dashboard'))
                
                else:
                    # Password incorrect
                    flash("Invalid password!", "error")
            else:
                flash("Your account was disactivated!", "error")
        else:
             flash("User not found!", "error")
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))



