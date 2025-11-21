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

def send_daily_reminder_email(user_email, username, new_lots=None, days_since=None):
    """Send daily reminder email to inactive users"""
    subject = "Daily Reminder - Vehicle Parking App"
    freshness = (
        f"You haven't visited in {days_since} day(s). " if days_since is not None else ""
    )
    new_lot_html = ""
    new_lot_text = ""
    if new_lots:
        lot_list = ", ".join(new_lots)
        new_lot_text = f"\nHot off the press: new lots have just been added ({lot_list}).\n"
        new_lot_html = f"<p>Hot off the press: new lots have just been added (<strong>{lot_list}</strong>).</p>"

    body = f"""
Hello {username},

{freshness}This is a reminder from the Vehicle Parking App.
{new_lot_text}Book a spot now!

Best regards,
Vehicle Parking App Team
    """
    html = f"""
    <html>
        <body>
            <h2>Daily Reminder - Vehicle Parking App</h2>
            <p>Hello {username},</p>
            <p>{freshness or "This is a quick reminder from the Vehicle Parking App."}</p>
            {new_lot_html}
            <p><strong>Book a spot now!</strong></p>
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
Completed Reservations: {report_data.get('completed_reservations', 0)}
Total Hours Parked: {report_data.get('total_hours', 0)}
Total Spent: ₹{report_data.get('total_spent', 0):.2f}
Most Used Lot: {report_data.get('most_used_lot', 'N/A')}

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
                <li><strong>Completed Reservations:</strong> {report_data.get('completed_reservations', 0)}</li>
                <li><strong>Total Hours Parked:</strong> {report_data.get('total_hours', 0)}</li>
                <li><strong>Total Spent:</strong> ₹{report_data.get('total_spent', 0):.2f}</li>
                <li><strong>Most Used Lot:</strong> {report_data.get('most_used_lot', 'N/A')}</li>
            </ul>
            <p>Best regards,<br>Vehicle Parking App Team</p>
        </body>
    </html>
    """
    return send_email(user_email, subject, body, html)

