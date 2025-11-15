"""
Celery Configuration File
This file helps Celery find the app and tasks
"""

from app import celery, app

# Make sure tasks are imported so Celery can discover them
from utils import tasks

# This ensures tasks are registered
__all__ = ['celery', 'app']

