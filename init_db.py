from app import create_app, db
from app.models.user import User, Role
from app.models.roster import Team, Player
from datetime import datetime, timezone

def init_database():
    app = create_app()
    
    with app.app_context():
        print('Creating database tables...')
        db.create_all()
        
        print('Inserting roles...')
        Role.insert_roles()
        
        print('Creating admin user...')
        admin = User.query.filter_by(username='admin').first()
        if admin is None:
            admin_role = Role.query.filter_by(name='Admin').first()
            admin = User(
                username='admin',
                email='admin@magallanes.datanalytics.pro',
                first_name='Admin',
                last_name='Magallanes',
                role=admin_role,
                confirmed=True,
                status='approved',
                active=True,
                approved_at=datetime.now(timezone.utc)
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: admin/admin123')
        
        print('Database initialized successfully!')

if __name__ == '__main__':
    init_database()