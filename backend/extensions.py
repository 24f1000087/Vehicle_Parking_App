"""
Extensions Module
Centralized place for Flask extensions to avoid circular imports
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail

# Initialize extensions (will be initialized with app in app.py)
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

