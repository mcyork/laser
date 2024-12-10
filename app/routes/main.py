# app/routes/main.py
from flask import Blueprint, render_template, jsonify
import sys
import flask
import platform

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('game.html')

@bp.route('/status')
def status():
    return jsonify({
        'system': 'Laser Maze Control System',
        'status': 'Active',
        'python_version': sys.version.split()[0],
        'flask_version': flask.__version__,
        'platform': platform.platform()
    })