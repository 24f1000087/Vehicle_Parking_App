"""
Celery Background Tasks
Handles async tasks: daily reminders, monthly reports, CSV export
"""

from app import celery
from models.user_model import User
from models.reservation_model import Reservation
from utils.mailer import send_daily_reminder_email, send_monthly_report_email
from datetime import datetime, timedelta
import csv
import io
import os

@celery.task(name='utils.tasks.send_daily_reminders')
def send_daily_reminders():
    """Send daily reminder emails to inactive users"""
    try:
        # Get users who haven't made a reservation in the last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        users = User.query.filter_by(role='user').all()
        sent_count = 0
        
        for user in users:
            # Check if user has recent reservations
            recent_reservation = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.created_at >= seven_days_ago
            ).first()
            
            # If no recent reservation, send reminder
            if not recent_reservation:
                # Note: In a real app, you'd store user email in the User model
                # For now, we'll use a placeholder
                user_email = f"{user.username}@example.com"  # Placeholder
                if send_daily_reminder_email(user_email, user.username):
                    sent_count += 1
        
        return f"Sent {sent_count} daily reminder emails"
    except Exception as e:
        return f"Error sending daily reminders: {str(e)}"

@celery.task(name='utils.tasks.send_monthly_reports')
def send_monthly_reports():
    """Send monthly report emails to all users"""
    try:
        # Get last month's date range
        now = datetime.utcnow()
        first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        
        users = User.query.filter_by(role='user').all()
        sent_count = 0
        
        for user in users:
            # Get user's reservations from last month
            reservations = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.created_at >= first_day_last_month,
                Reservation.created_at <= last_day_last_month
            ).all()
            
            # Calculate report data
            total_reservations = len(reservations)
            active_reservations = len([r for r in reservations if r.status == 'active'])
            total_spent = sum([r.cost for r in reservations if r.cost]) or 0
            
            report_data = {
                'total_reservations': total_reservations,
                'active_reservations': active_reservations,
                'total_spent': total_spent
            }
            
            # Note: In a real app, you'd store user email in the User model
            user_email = f"{user.username}@example.com"  # Placeholder
            if send_monthly_report_email(user_email, user.username, report_data):
                sent_count += 1
        
        return f"Sent {sent_count} monthly report emails"
    except Exception as e:
        return f"Error sending monthly reports: {str(e)}"

@celery.task(name='utils.tasks.export_reservations_csv')
def export_reservations_csv(user_id):
    """Export user's reservations as CSV file (async)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return "User not found"
        
        # Get all reservations
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(
            Reservation.created_at.desc()
        ).all()
        
        # Create CSV file
        filename = f"reservations_{user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
        filepath = os.path.join('exports', filename)
        
        # Create exports directory if it doesn't exist
        os.makedirs('exports', exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'Reservation ID',
                'Spot Number',
                'Lot Name',
                'Start Time',
                'End Time',
                'Cost',
                'Status',
                'Created At'
            ])
            
            # Write data
            for res in reservations:
                writer.writerow([
                    res.id,
                    res.parking_spot.spot_number if res.parking_spot else 'N/A',
                    res.parking_spot.parking_lot.name if res.parking_spot and res.parking_spot.parking_lot else 'N/A',
                    res.start_time.isoformat() if res.start_time else 'N/A',
                    res.end_time.isoformat() if res.end_time else 'N/A',
                    res.cost or 'N/A',
                    res.status,
                    res.created_at.isoformat() if res.created_at else 'N/A'
                ])
        
        return f"CSV exported to {filepath}"
    except Exception as e:
        return f"Error exporting CSV: {str(e)}"

