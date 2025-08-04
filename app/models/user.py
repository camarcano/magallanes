from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app.models.permissions import Permission

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
    
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm
    
    def reset_permissions(self):
        self.permissions = 0
    
    def has_permission(self, perm):
        return self.permissions & perm == perm
    
    @staticmethod
    def insert_roles():
        roles = {
            'Regular': [Permission.VIEW_BASIC_STATS],
            'Analyst': [Permission.VIEW_BASIC_STATS, Permission.VIEW_ADVANCED_STATS, 
                       Permission.EXPORT_DATA],
            'Manager': [Permission.VIEW_BASIC_STATS, Permission.VIEW_ADVANCED_STATS,
                       Permission.EXPORT_DATA, Permission.MANAGE_TEAMS, 
                       Permission.MANAGE_USERS, Permission.MANAGE_ANALYSTS],
            'Admin': [Permission.VIEW_BASIC_STATS, Permission.VIEW_ADVANCED_STATS,
                     Permission.EXPORT_DATA, Permission.MANAGE_TEAMS, 
                     Permission.MANAGE_USERS, Permission.MANAGE_ANALYSTS,
                     Permission.MANAGE_MANAGERS, Permission.ADMIN]
        }
        
        default_role = 'Regular'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    confirmed = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='approved')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    approved_at = db.Column(db.DateTime)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    approved_by = db.relationship('User', remote_side=[id])
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == 'admin@magallanes.datanalytics.pro':
                self.role = Role.query.filter_by(name='Admin').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)
    
    def is_admin(self):
        return self.can(Permission.ADMIN)
    
    def can_manage_user(self, user):
        """Check if current user can manage target user"""
        if not self.can(Permission.MANAGE_USERS):
            return False
        
        # Admin can manage everyone
        if self.is_admin():
            return True
        
        # Manager can manage Analysts and Regular users
        if self.can(Permission.MANAGE_MANAGERS):
            return user.role.name in ['Regular', 'Analyst', 'Manager']
        
        # Analyst can manage Regular users only
        if self.can(Permission.MANAGE_ANALYSTS):
            return user.role.name == 'Regular'
        
        return False