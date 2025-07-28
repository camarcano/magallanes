from flask import Blueprint

bp = Blueprint('roster', __name__)

from app.roster import routes