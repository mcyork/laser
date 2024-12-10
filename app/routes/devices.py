# app/routes/devices.py
from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime
import json

bp = Blueprint('devices', __name__, url_prefix='/api/devices')

# In-memory storage for connected devices
# In production this should be a proper database
devices = {}

@bp.route('/checkin', methods=['POST'])
def device_checkin():
    """
    Handle device check-in requests
    Expected payload:
    {
        "guid": "uuid-string-here",  # Optional - if missing, we assign one
        "firmware_version": "1.0.0",
        "capabilities": ["LED1", "LED2", "LED3", "LED4"],
        "ip_address": "192.168.1.100"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # If no GUID, this is a new device requesting one
    if 'guid' not in data:
        new_guid = str(uuid.uuid4())
        response = {
            "guid": new_guid,
            "status": "registered"
        }
        data['guid'] = new_guid
    else:
        response = {
            "status": "acknowledged"
        }
    
    # Update device info with timestamp
    devices[data['guid']] = {
        "firmware_version": data.get('firmware_version', 'unknown'),
        "capabilities": data.get('capabilities', []),
        "ip_address": data.get('ip_address'),
        "last_seen": datetime.utcnow().isoformat(),
        "first_seen": devices.get(data['guid'], {}).get('first_seen', datetime.utcnow().isoformat())
    }
    
    return jsonify(response)

@bp.route('/list', methods=['GET'])
def list_devices():
    """Return list of known devices and their status"""
    # Calculate active status (seen in last 5 minutes)
    current_time = datetime.utcnow()
    active_devices = []
    
    for guid, info in devices.items():
        last_seen = datetime.fromisoformat(info['last_seen'])
        time_diff = (current_time - last_seen).total_seconds()
        
        active_devices.append({
            "guid": guid,
            "status": "active" if time_diff < 300 else "inactive",
            "firmware_version": info['firmware_version'],
            "capabilities": info['capabilities'],
            "ip_address": info['ip_address'],
            "last_seen": info['last_seen'],
            "first_seen": info['first_seen']
        })
    
    return jsonify(active_devices)

@bp.route('/command', methods=['POST'])
def send_command():
    """
    Send command to specific device(s)
    Expected payload:
    {
        "guid": "device-guid" or ["guid1", "guid2"] for multiple devices,
        "command": "update_available",
        "data": {
            "version": "1.1.0",
            "url": "https://our-server/firmware/v1.1.0.bin"
        }
    }
    """
    data = request.get_json()
    
    if not data or 'guid' not in data or 'command' not in data:
        return jsonify({"error": "Missing required fields"}), 400
        
    target_guids = data['guid'] if isinstance(data['guid'], list) else [data['guid']]
    unknown_devices = [guid for guid in target_guids if guid not in devices]
    
    if unknown_devices:
        return jsonify({
            "error": "Unknown devices",
            "devices": unknown_devices
        }), 404
    
    # For now, just simulate command sending
    # In reality, we'd need to actually send commands to the devices
    return jsonify({
        "status": "commands_queued",
        "devices": target_guids
    })

# Optional: Cleanup endpoint for testing
@bp.route('/cleanup', methods=['POST'])
def cleanup_inactive():
    """Remove devices not seen in last hour"""
    current_time = datetime.utcnow()
    inactive_guids = []
    
    for guid, info in list(devices.items()):  # list() to avoid runtime modification issues
        last_seen = datetime.fromisoformat(info['last_seen'])
        if (current_time - last_seen).total_seconds() > 3600:  # 1 hour
            inactive_guids.append(guid)
            del devices[guid]
    
    return jsonify({
        "removed_devices": inactive_guids,
        "count": len(inactive_guids)
    })