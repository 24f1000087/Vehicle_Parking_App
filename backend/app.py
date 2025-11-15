"""
Vehicle Parking App - Backend Main Application
Setup Instructions:
1. Install dependencies: pip install flask flask-sqlalchemy flask-cors flask-jwt-extended redis celery flask-mail
2. Make sure Redis is running: redis-server
3. Run Celery worker: celery -A app.celery worker --loglevel=info
4. Run Celery beat (for scheduled tasks): celery -A app.celery beat --loglevel=info
5. Run Flask app: flask run
"""

from flask import Flask
from flask_cors import CORS
from celery import Celery
import redis
from datetime import timedelta
import os

# Import extensions (defined in extensions.py to avoid circular imports)
from extensions import db, jwt, mail

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///parking_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Flask-Mail configuration (Gmail SMTP)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-app-password')

# Redis configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Celery configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)

# Initialize extensions with app
db.init_app(app)
CORS(app)  # Enable CORS for frontend
jwt.init_app(app)
mail.init_app(app)

# Initialize Redis client
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Initialize Celery
celery = Celery(
    'app',  # Use string name instead of app.import_name
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'daily-reminder': {
            'task': 'utils.tasks.send_daily_reminders',
            'schedule': timedelta(days=1),
        },
        'monthly-report': {
            'task': 'utils.tasks.send_monthly_reports',
            'schedule': timedelta(days=30),
        },
    }
)

# Import models (must be after db initialization)
from models.user_model import User
from models.parkinglot_model import ParkingLot
from models.parkingspot_model import ParkingSpot
from models.reservation_model import Reservation

# Import routes
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.user_routes import user_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(user_bp, url_prefix='/api/user')

# Initialize database on app start
with app.app_context():
    db.create_all()
    
    # Create default admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: username='admin', password='admin123'")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'ok', 'message': 'Vehicle Parking App API is running'}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)

