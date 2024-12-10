# app/routes/admin.py
from flask import Blueprint, render_template, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
def index():
    return render_template('admin/index.html')

@bp.route('/settings')
def settings():
    return render_template('admin/settings.html')

@bp.route('/docs')
def documentation():
    return render_template('admin/documentation.html')

# Configuration for firmware uploads
ALLOWED_EXTENSIONS = {'bin'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/firmware', methods=['GET'])
def firmware_list():
    """List all available firmware versions"""
    firmware_dir = os.path.join(current_app.root_path, 'firmware')
    if not os.path.exists(firmware_dir):
        os.makedirs(firmware_dir)
    
    firmware_files = []
    for file in os.listdir(firmware_dir):
        if file.endswith('.bin'):
            file_path = os.path.join(firmware_dir, file)
            stat = os.stat(file_path)
            firmware_files.append({
                'filename': file,
                'size': stat.st_size,
                'uploaded_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'version': file.split('-')[1] if '-' in file else 'unknown'
            })
    
    return jsonify(firmware_files)

@bp.route('/firmware/upload', methods=['POST'])
def upload_firmware():
    """Handle firmware file uploads"""
    if 'firmware' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['firmware']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        firmware_dir = os.path.join(current_app.root_path, 'firmware')
        
        if not os.path.exists(firmware_dir):
            os.makedirs(firmware_dir)
        
        file_path = os.path.join(firmware_dir, filename)
        file.save(file_path)
        
        return jsonify({
            'message': 'Firmware uploaded successfully',
            'filename': filename
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@bp.route('/devices', methods=['GET'])
def list_devices():
    """List all connected devices"""
    # TODO: Implement actual device discovery
    # For now, return mock data for Proto 1
    devices = [
        {
            'id': 'proto1-001',
            'name': 'Prototype 1 Board',
            'status': 'connected',
            'firmware_version': '0.1.0',
            'capabilities': ['LED1', 'LED2', 'LED3', 'LED4']
        }
    ]
    return jsonify(devices)

@bp.route('/firmware/<filename>', methods=['DELETE'])
def delete_firmware(filename):
    """Delete a firmware file"""
    try:
        firmware_path = os.path.join(current_app.root_path, 'firmware', secure_filename(filename))
        if os.path.exists(firmware_path):
            os.remove(firmware_path)
            return jsonify({'message': 'Firmware deleted successfully'})
        return jsonify({'error': 'Firmware not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/firmware/deploy', methods=['POST'])
def deploy_firmware():
    """Deploy firmware to selected devices"""
    data = request.get_json()
    if not data or 'firmware' not in data or 'devices' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    firmware = data['firmware']
    devices = data['devices']
    
    # TODO: Implement actual deployment logic
    # This would involve:
    # 1. Verifying firmware exists
    # 2. Checking device availability
    # 3. Initiating OTA update process
    # 4. Monitoring update progress
    # 5. Reporting results
    
    return jsonify({
        'message': 'Deployment initiated',
        'firmware': firmware,
        'devices': devices,
        'status': 'pending'
    })