from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, IntegerField, SelectField, TextAreaField, SubmitField, DecimalField, DateField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
from app.models.roster import Player

class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired(), Length(min=2, max=100)])
    league = StringField('League', validators=[Optional(), Length(max=50)])
    division = StringField('Division', validators=[Optional(), Length(max=50)])
    city = StringField('City', validators=[Optional(), Length(max=50)])
    state = StringField('State/Province', validators=[Optional(), Length(max=50)])
    country = StringField('Country', validators=[Optional(), Length(max=50)])
    founded_year = IntegerField('Founded Year', validators=[Optional(), NumberRange(min=1800, max=2100)])
    home_stadium = StringField('Home Stadium', validators=[Optional(), Length(max=100)])
    manager = StringField('Manager', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Team')

class PlayerForm(FlaskForm):
    name = StringField('Player Name', validators=[DataRequired(), Length(min=2, max=100)])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    general_position = SelectField('General Position', validators=[Optional()], choices=[
        ('', 'Select General Position'),
        ('CATCHER', 'Catcher'),
        ('INFIELDER', 'Infielder'),
        ('OUTFIELDER', 'Outfielder'),
        ('RHP', 'Right-Handed Pitcher'),
        ('LHP', 'Left-Handed Pitcher'),
        ('PITCHER', 'Pitcher (General)')
    ])
    specific_position = SelectField('Specific Position', validators=[Optional()], choices=[
        ('', 'Select Specific Position'),
        ('C', 'Catcher (C)'), ('1B', 'First Base (1B)'), ('2B', 'Second Base (2B)'),
        ('3B', 'Third Base (3B)'), ('SS', 'Shortstop (SS)'), ('LF', 'Left Field (LF)'),
        ('CF', 'Center Field (CF)'), ('RF', 'Right Field (RF)'), ('DH', 'Designated Hitter (DH)'),
        ('SP', 'Starting Pitcher (SP)'), ('RP', 'Relief Pitcher (RP)'), ('CP', 'Closing Pitcher (CP)')
    ])
    jersey_number = IntegerField('Jersey Number', validators=[Optional(), NumberRange(min=0, max=99)])
    birthplace_city = StringField('Birthplace City', validators=[Optional(), Length(max=50)])
    birthplace_state = StringField('State/Region Code', validators=[Optional(), Length(max=10)])
    height = StringField('Height', validators=[Optional(), Length(max=10)])
    weight = IntegerField('Weight (lbs)', validators=[Optional(), NumberRange(min=100, max=400)])
    bats = SelectField('Bats', validators=[Optional()], choices=[
        ('', 'Select'), ('LEFT', 'Left'), ('RIGHT', 'Right'), ('SWITCH', 'Switch')
    ])
    throws = SelectField('Throws', validators=[Optional()], choices=[
        ('', 'Select'), ('LEFT', 'Left'), ('RIGHT', 'Right')
    ])
    current_league = StringField('Current League', validators=[Optional(), Length(max=50)])
    current_team_external = StringField('External Team', validators=[Optional(), Length(max=100)])
    contract_status = SelectField('Contract Status', validators=[Optional()], choices=[
        ('', 'Select Status'), ('Active', 'Active'), ('Free Agent', 'Free Agent'),
        ('Minor League', 'Minor League'), ('Retired', 'Retired')
    ])
    salary = DecimalField('Annual Salary ($)', validators=[Optional(), NumberRange(min=0)], places=2)
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Save Player')

class CSVImportForm(FlaskForm):
    csv_file = FileField('CSV File', validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
    submit = SubmitField('Import Players')