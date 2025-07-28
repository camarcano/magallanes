from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.admin import bp
from app.admin.forms import UserCreateForm, UserEditForm
from app.models.user import User, Role
from app.utils.decorators import admin_required

@bp.route('/')
@login_required
@admin_required
def index():
    total_users = User.query.count()
    pending_users = User.query.filter_by(status='pending').count()
    active_users = User.query.filter_by(status='approved', active=True).count()
    recent_registrations = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html', 
                         title='Admin Dashboard',
                         total_users=total_users,
                         pending_users=pending_users,
                         active_users=active_users,
                         recent_registrations=recent_registrations)

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users)

@bp.route('/user/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = UserCreateForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            department=form.department.data,
            role_id=form.role.data,
            status='approved',
            active=True,
            approved_by=current_user
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.username} has been created successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, is_edit=False)