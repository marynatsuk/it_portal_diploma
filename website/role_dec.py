from functools import wraps
from flask_login import current_user
from flask import abort, redirect, url_for
#multiple roles
def role_required(roles):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            user_role_id = current_user.role_id
            if user_role_id not in roles:
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator
