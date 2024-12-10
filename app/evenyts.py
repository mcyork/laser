# app/events.py
from flask_socketio import emit
from app import socketio

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('laser_event', {'type': 'status', 'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_game')
def handle_start_game():
    emit('laser_event', {'type': 'game_start', 'message': 'Game started'})

@socketio.on('stop_game')
def handle_stop_game():
    emit('laser_event', {'type': 'game_stop', 'message': 'Game stopped'})

# Test event for laser break
@socketio.on('test_laser_break')
def handle_test_laser_break(data):
    emit('laser_event', {
        'type': 'laser_break',
        'laser': data.get('laser', 1)
    })