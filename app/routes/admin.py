# app/routes/admin.py
from flask import Blueprint, render_template

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
def index():
    return render_template('admin/index.html')

@bp.route('/settings')
def settings():
    return render_template('admin/settings.html')