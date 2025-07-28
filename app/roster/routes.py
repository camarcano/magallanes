from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, session
from flask_login import login_required, current_user
from app import db
from app.roster import bp
from app.roster.forms import TeamForm, PlayerForm, CSVImportForm
from app.models.roster import Team, Player
from app.utils.decorators import admin_required
import csv
import io
from datetime import datetime

@bp.route('/')
@login_required
def index():
    teams = Team.query.order_by(Team.name).all()
    total_teams = len(teams)
    total_players = Player.query.count()
    recent_players = Player.query.order_by(Player.created_at.desc()).limit(5).all()
    
    return render_template('roster/index.html',
                         teams=teams,
                         total_teams=total_teams,
                         total_players=total_players,
                         recent_players=recent_players)

@bp.route('/teams')
@login_required
def teams():
    page = request.args.get('page', 1, type=int)
    teams = Team.query.order_by(Team.name).paginate(
        page=page, per_page=12, error_out=False)
    return render_template('roster/teams.html', teams=teams)

@bp.route('/team/<int:team_id>')
@login_required
def team_detail(team_id):
    team = Team.query.get_or_404(team_id)
    positions = {}
    for player in team.players:
        pos = player.general_position or 'Unknown'
        if pos not in positions:
            positions[pos] = []
        positions[pos].append(player)
    
    position_order = ['CATCHER', 'INFIELDER', 'OUTFIELDER', 'RHP', 'LHP', 'PITCHER']
    ordered_positions = []
    for pos in position_order:
        if pos in positions:
            ordered_positions.append((pos, positions[pos]))
    
    for pos, players in positions.items():
        if pos not in position_order:
            ordered_positions.append((pos, players))
    
    return render_template('roster/team_detail.html',
                         team=team,
                         ordered_positions=ordered_positions)

@bp.route('/team/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_team():
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(
            name=form.name.data,
            league=form.league.data,
            division=form.division.data,
            city=form.city.data,
            state=form.state.data,
            country=form.country.data,
            founded_year=form.founded_year.data,
            home_stadium=form.home_stadium.data,
            manager=form.manager.data,
            description=form.description.data,
            created_by=current_user
        )
        db.session.add(team)
        db.session.commit()
        flash(f'Team "{team.name}" has been created successfully!', 'success')
        return redirect(url_for('roster.team_detail', team_id=team.id))
    
    return render_template('roster/team_form.html', 
                         form=form, title='Create New Team')

@bp.route('/team/<int:team_id>/add_player', methods=['GET', 'POST'])
@login_required
def add_player(team_id):
    team = Team.query.get_or_404(team_id)
    form = PlayerForm()
    
    if form.validate_on_submit():
        player = Player(
            name=form.name.data,
            date_of_birth=form.date_of_birth.data,
            general_position=form.general_position.data,
            specific_position=form.specific_position.data,
            jersey_number=form.jersey_number.data,
            height=form.height.data,
            weight=form.weight.data,
            bats=form.bats.data,
            throws=form.throws.data,
            current_league=form.current_league.data,
            current_team_external=form.current_team_external.data,
            contract_status=form.contract_status.data,
            salary=form.salary.data,
            notes=form.notes.data,
            team=team,
            created_by=current_user
        )
        
        if form.birthplace_city.data or form.birthplace_state.data:
            if form.birthplace_city.data and form.birthplace_state.data:
                player.birthplace_full = f"{form.birthplace_city.data} - {form.birthplace_state.data}"
            else:
                player.birthplace_full = form.birthplace_city.data or form.birthplace_state.data
            player.birthplace_city = form.birthplace_city.data
            player.birthplace_state = form.birthplace_state.data
        
        db.session.add(player)
        db.session.commit()
        flash(f'Player "{player.name}" has been added to {team.name}!', 'success')
        return redirect(url_for('roster.team_detail', team_id=team_id))
    
    return render_template('roster/player_form.html',
                         form=form, team=team, title=f'Add Player to {team.name}')

@bp.route('/team/<int:team_id>/import_players', methods=['GET', 'POST'])
@login_required
def import_players(team_id):
    team = Team.query.get_or_404(team_id)
    form = CSVImportForm()
    
    if form.validate_on_submit():
        file = form.csv_file.data
        
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            imported_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    name = row.get('Player name', '').strip()
                    if not name:
                        errors.append(f"Row {row_num}: Player name is required")
                        continue
                    
                    existing_player = Player.query.filter_by(
                        name=name, team_id=team_id
                    ).first()
                    
                    if existing_player:
                        errors.append(f"Row {row_num}: Player '{name}' already exists in this team")
                        continue
                    
                    player = Player(
                        name=name,
                        general_position=row.get('General Position', '').strip() or None,
                        specific_position=row.get('Specific POS', '').strip() or None,
                        bats=row.get('Bats', '').strip() or None,
                        throws=row.get('Throws', '').strip() or None,
                        current_league=row.get('Actual League', '').strip() or None,
                        current_team_external=row.get('Team', '').strip() or None,
                        team=team,
                        created_by=current_user
                    )
                    
                    birthplace = row.get('Birthplace', '').strip()
                    if birthplace:
                        player.set_birthplace_from_string(birthplace)
                    
                    dob_str = row.get('DOB', '').strip()
                    if dob_str:
                        try:
                            player.set_date_of_birth_from_string(dob_str)
                        except Exception:
                            errors.append(f"Row {row_num}: Invalid date format '{dob_str}' for player '{name}'")
                            continue
                    
                    db.session.add(player)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: Error processing player - {str(e)}")
            
            if imported_count > 0:
                db.session.commit()
                flash(f'Successfully imported {imported_count} players to {team.name}!', 'success')
            
            for error in errors[:10]:
                flash(error, 'warning')
            if len(errors) > 10:
                flash(f'... and {len(errors) - 10} more errors', 'warning')
            
            if imported_count > 0:
                return redirect(url_for('roster.team_detail', team_id=team_id))
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing CSV file: {str(e)}', 'danger')
            current_app.logger.error(f'CSV import error: {e}', exc_info=True)
    
    return render_template('roster/import_players.html', form=form, team=team)