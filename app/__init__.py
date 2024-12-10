# app/__init__.py
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import logging

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()  # Create SocketIO instance

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)  # Initialize SocketIO with app
    
    # Register blueprints
    from app.routes import main, admin, devices
    app.register_blueprint(main.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(devices.bp)
    
    return app

def setup_firmware_logging():
    logger = logging.getLogger('firmware')
    handler = logging.FileHandler('firmware.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger