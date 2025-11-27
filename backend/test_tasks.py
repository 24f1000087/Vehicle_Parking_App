from app import app
from utils.tasks import send_daily_reminders, send_monthly_reports

if __name__ == "__main__":
    with app.app_context():
        print(send_daily_reminders.run())
        print(send_monthly_reports.run())