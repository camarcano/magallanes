from app import create_app, db
from app.models.user import User, Role
from app.models.roster import Team, Player

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role, 'Team': Team, 'Player': Player}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)