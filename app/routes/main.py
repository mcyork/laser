from flask import Blueprint, render_template
import sys
import flask
import platform

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return {
        'system': 'Laser Maze Development Environment',
        'status': 'Active',
        'python_version': sys.version.split()[0],
        'flask_version': flask.__version__,
        'platform': platform.platform()
    }
