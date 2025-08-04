from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from app.models.user import User, Role
from flask_login import current_user

class UserCreateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone')
    department = StringField('Department')
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Create User')
    
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.populate_roles()
    
    def populate_roles(self):
        """Populate role choices based on current user permissions"""
        if current_user.is_admin():
            roles = Role.query.all()
        elif current_user.can_manage_user(User(role=Role(name='Manager'))):
            roles = Role.query.filter(Role.name.in_(['Regular', 'Analyst', 'Manager'])).all()
        elif current_user.can_manage_user(User(role=Role(name='Analyst'))):
            roles = Role.query.filter(Role.name.in_(['Regular', 'Analyst'])).all()
        else:
            roles = Role.query.filter_by(name='Regular').all()
        
        self.role.choices = [(role.id, role.name) for role in roles]
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists.')

class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone')
    department = StringField('Department')
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Update User')
    
    def __init__(self, user, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.user = user
        self.populate_roles()
    
    def populate_roles(self):
        """Populate role choices based on current user permissions"""
        if current_user.is_admin():
            roles = Role.query.all()
        elif current_user.can_manage_user(User(role=Role(name='Manager'))):
            roles = Role.query.filter(Role.name.in_(['Regular', 'Analyst', 'Manager'])).all()
        elif current_user.can_manage_user(User(role=Role(name='Analyst'))):
            roles = Role.query.filter(Role.name.in_(['Regular', 'Analyst'])).all()
        else:
            roles = Role.query.filter_by(name='Regular').all()
        
        self.role.choices = [(role.id, role.name) for role in roles]
    
    def validate_username(self, username):
        if username.data != self.user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists.')
    
    def validate_email(self, email):
        if email.data != self.user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already exists.')