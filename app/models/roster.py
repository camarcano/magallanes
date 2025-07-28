from app import db
from datetime import datetime, timezone
import uuid
from dateutil.relativedelta import relativedelta
import re
from sqlalchemy.ext.hybrid import hybrid_property

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    league = db.Column(db.String(50))
    division = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    founded_year = db.Column(db.Integer)
    home_stadium = db.Column(db.String(100))
    manager = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), 
                          onupdate=datetime.now(timezone.utc))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_by = db.relationship('User', backref='created_teams')
    players = db.relationship('Player', backref='team', lazy='dynamic', 
                            cascade='all, delete-orphan')
    
    @property
    def player_count(self):
        return self.players.count()
    
    @property
    def average_age(self):
        ages = [p.age for p in self.players if p.age]
        return round(sum(ages) / len(ages), 1) if ages else None

class Player(db.Model):
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    player_slug = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False, index=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    jersey_number = db.Column(db.Integer)
    general_position = db.Column(db.String(20), index=True)
    specific_position = db.Column(db.String(10), index=True)
    birthplace_city = db.Column(db.String(50))
    birthplace_state = db.Column(db.String(10))
    birthplace_full = db.Column(db.String(100))
    height = db.Column(db.String(10))
    weight = db.Column(db.Integer)
    bats = db.Column(db.String(10))
    throws = db.Column(db.String(10))
    current_league = db.Column(db.String(50))
    current_team_external = db.Column(db.String(100))
    contract_status = db.Column(db.String(50))
    salary = db.Column(db.Numeric(12, 2))
    field_x = db.Column(db.Float, default=0.0)
    field_y = db.Column(db.Float, default=0.0)
    depth_order = db.Column(db.Integer, default=1)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), 
                          onupdate=datetime.now(timezone.utc))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_by = db.relationship('User', backref='created_players')
    
    __table_args__ = (
        db.UniqueConstraint('team_id', 'jersey_number', name='unique_jersey_per_team'),
    )
    
    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)
        if not self.player_slug and self.name:
            self.player_slug = self.generate_slug()
    
    def generate_slug(self):
        if not self.name:
            return str(uuid.uuid4())[:8]
        slug_base = re.sub(r'[^a-zA-Z0-9\s-]', '', self.name.lower())
        slug_base = re.sub(r'\s+', '-', slug_base.strip())
        counter = 1
        slug = slug_base
        while Player.query.filter_by(player_slug=slug).first():
            slug = f"{slug_base}-{counter}"
            counter += 1
        return slug
    
    @hybrid_property
    def age(self):
        if not self.date_of_birth:
            return None
        today = datetime.now().date()
        return relativedelta(today, self.date_of_birth).years
    
    @property
    def birthplace_display(self):
        if self.birthplace_full:
            return self.birthplace_full
        elif self.birthplace_city and self.birthplace_state:
            return f"{self.birthplace_city} - {self.birthplace_state}"
        elif self.birthplace_city:
            return self.birthplace_city
        return None
    
    @property
    def position_display(self):
        position_map = {
            'C': 'Catcher', '1B': 'First Base', '2B': 'Second Base', 
            '3B': 'Third Base', 'SS': 'Shortstop', 'LF': 'Left Field',
            'CF': 'Center Field', 'RF': 'Right Field', 'DH': 'Designated Hitter',
            'SP': 'Starting Pitcher', 'RP': 'Relief Pitcher', 'CP': 'Closing Pitcher',
            'RHP': 'Right-Handed Pitcher', 'LHP': 'Left-Handed Pitcher'
        }
        if self.specific_position:
            return position_map.get(self.specific_position, self.specific_position)
        elif self.general_position:
            return self.general_position.title()
        return 'Unknown'
    
    def set_date_of_birth_from_string(self, dob_string, format='%d/%m/%Y'):
        try:
            self.date_of_birth = datetime.strptime(dob_string, format).date()
        except ValueError:
            try:
                self.date_of_birth = datetime.strptime(dob_string, '%m/%d/%Y').date()
            except ValueError:
                try:
                    self.date_of_birth = datetime.strptime(dob_string, '%Y-%m-%d').date()
                except ValueError:
                    pass
    
    def set_birthplace_from_string(self, birthplace_string):
        self.birthplace_full = birthplace_string
        if ' - ' in birthplace_string:
            parts = birthplace_string.split(' - ', 1)
            self.birthplace_city = parts[0].strip()
            self.birthplace_state = parts[1].strip()
        else:
            self.birthplace_city = birthplace_string.strip()