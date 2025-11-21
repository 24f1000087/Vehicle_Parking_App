"""
Extensions Module
Centralized place for Flask extensions to avoid circular imports
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from flask_mail import Mail
from flask import jsonify
from functools import wraps
import redis

# Initialize extensions (will be initialized with app in app.py)
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
redis_client = None

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Custom response for expired tokens"""
    return jsonify({
        'status': 'error',
        'message': 'Token has expired',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
@jwt.unauthorized_loader
def invalid_token_callback(error):
    print(f"[JWT ERROR] {error}")
    """Custom response for invalid tokens"""
    return jsonify({
        'status': 'error',
        'message': 'Invalid or missing token',
        'error': 'invalid_token'
    }), 401

def admin_required(fn):
    """Decorator to require admin access"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Admin access required',
                'error': 'forbidden'
            }), 403
        return fn(*args, **kwargs)
    return wrapper

def init_extensions(app):
    """Initialize all extensions with the app"""
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize JWT
    jwt.init_app(app)
    
    # Initialize Mail
    mail.init_app(app)
    
    # Initialize Redis
    global redis_client
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    redis_client = redis.from_url(redis_url, decode_responses=True)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
