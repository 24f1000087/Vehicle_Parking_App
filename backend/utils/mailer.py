"""
Email Utilities
Handles sending emails using Flask-Mail
"""

from extensions import mail
from flask_mail import Message
from flask import current_app

def send_email(to, subject, body, html=None):
    """
    Send an email
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Plain text body
        html: HTML body (optional)
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            body=body,
            html=html
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_daily_reminder_email(user_email, username):
    """Send daily reminder email to inactive users"""
    subject = "Daily Reminder - Vehicle Parking App"
    body = f"""
Hello {username},

This is a daily reminder from the Vehicle Parking App.
You haven't made any reservations recently. Book a spot now!

Best regards,
Vehicle Parking App Team
    """
    html = f"""
    <html>
        <body>
            <h2>Daily Reminder - Vehicle Parking App</h2>
            <p>Hello {username},</p>
            <p>This is a daily reminder from the Vehicle Parking App.</p>
            <p>You haven't made any reservations recently. <strong>Book a spot now!</strong></p>
            <p>Best regards,<br>Vehicle Parking App Team</p>
        </body>
    </html>
    """
    return send_email(user_email, subject, body, html)

def send_monthly_report_email(user_email, username, report_data):
    """Send monthly report email"""
    subject = "Monthly Report - Vehicle Parking App"
    body = f"""
Hello {username},

Here is your monthly parking usage report:

Total Reservations: {report_data.get('total_reservations', 0)}
Active Reservations: {report_data.get('active_reservations', 0)}
Total Spent: ${report_data.get('total_spent', 0):.2f}

Best regards,
Vehicle Parking App Team
    """
    html = f"""
    <html>
        <body>
            <h2>Monthly Report - Vehicle Parking App</h2>
            <p>Hello {username},</p>
            <p>Here is your monthly parking usage report:</p>
            <ul>
                <li><strong>Total Reservations:</strong> {report_data.get('total_reservations', 0)}</li>
                <li><strong>Active Reservations:</strong> {report_data.get('active_reservations', 0)}</li>
                <li><strong>Total Spent:</strong> ${report_data.get('total_spent', 0):.2f}</li>
            </ul>
            <p>Best regards,<br>Vehicle Parking App Team</p>
        </body>
    </html>
    """
    return send_email(user_email, subject, body, html)

