# app/routes/admin.py
from flask import Blueprint, render_template, request, jsonify, current_app, abort, send_file
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import hashlib
import json

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Existing routes remain the same
@bp.route('/')
def index():
    return render_template('admin/index.html')

@bp.route('/settings')
def settings():
    return render_template('admin/settings.html')

# Firmware Management
ALLOWED_EXTENSIONS = {'bin'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_firmware_info(filepath):
    """Get firmware file information including hash"""
    stat = os.stat(filepath)
    with open(filepath, 'rb') as f:
        content = f.read()
        sha256 = hashlib.sha256(content).hexdigest()
    
    # Try to get version from metadata file if it exists
    metadata_path = f"{filepath}.json"
    version = "unknown"
    description = ""
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                version = metadata.get('version', version)
                description = metadata.get('description', description)
        except json.JSONDecodeError:
            pass

    return {
        'filename': os.path.basename(filepath),
        'size': stat.st_size,
        'uploaded_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'sha256': sha256,
        'version': version,
        'description': description
    }

@bp.route('/firmware', methods=['GET'])
def firmware_list():
    """List all available firmware files"""
    firmware_dir = current_app.config['FIRMWARE_DIR']
    if not os.path.exists(firmware_dir):
        os.makedirs(firmware_dir)
    
    firmware_files = []
    for filename in os.listdir(firmware_dir):
        if filename.endswith('.bin'):
            filepath = os.path.join(firmware_dir, filename)
            firmware_files.append(get_firmware_info(filepath))
    
    # Sort by upload date, newest first
    firmware_files.sort(key=lambda x: x['uploaded_at'], reverse=True)
    return jsonify(firmware_files)

@bp.route('/firmware/upload', methods=['POST'])
def upload_firmware():
    """Handle firmware file uploads with metadata"""
    if 'firmware' not in request.files:
        return jsonify({'error': 'No firmware file provided'}), 400
    
    file = request.files['firmware']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filename = secure_filename(file.filename)
    firmware_dir = current_app.config['FIRMWARE_DIR']
    
    if not os.path.exists(firmware_dir):
        os.makedirs(firmware_dir)
    
    filepath = os.path.join(firmware_dir, filename)
    file.save(filepath)
    
    # Save metadata if provided
    metadata = {
        'version': request.form.get('version', 'unknown'),
        'description': request.form.get('description', ''),
        'uploaded_at': datetime.utcnow().isoformat(),
        'target_devices': request.form.getlist('target_devices')
    }
    
    metadata_path = f"{filepath}.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    firmware_info = get_firmware_info(filepath)
    return jsonify({
        'message': 'Firmware uploaded successfully',
        'firmware': firmware_info
    })

@bp.route('/firmware/<filename>')
def download_firmware(filename):
    """Download a specific firmware file"""
    firmware_dir = current_app.config['FIRMWARE_DIR']
    filepath = os.path.join(firmware_dir, secure_filename(filename))
    
    if not os.path.exists(filepath):
        abort(404)
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='application/octet-stream'
    )

@bp.route('/firmware/<filename>', methods=['DELETE'])
def delete_firmware(filename):
    """Delete a firmware file and its metadata"""
    firmware_dir = current_app.config['FIRMWARE_DIR']
    filepath = os.path.join(firmware_dir, secure_filename(filename))
    metadata_path = f"{filepath}.json"
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Firmware not found'}), 404
    
    try:
        os.remove(filepath)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        
        return jsonify({
            'message': 'Firmware deleted successfully',
            'filename': filename
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to delete firmware: {str(e)}'
        }), 500

@bp.route('/docs')
def documentation():
    """Documentation page route"""
    return render_template('admin/documentation.html')