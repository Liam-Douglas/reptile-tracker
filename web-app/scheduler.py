"""
Background Scheduler for Reptile Tracker
Handles automated feeding reminders and notifications
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Manages scheduled tasks for feeding reminders"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("Reminder scheduler started")
    
    def setup_daily_check(self, check_time='09:00'):
        """
        Set up daily check for feeding reminders
        Args:
            check_time: Time to check (HH:MM format)
        """
        hour, minute = map(int, check_time.split(':'))
        
        # Remove existing job if any
        if self.scheduler.get_job('daily_reminder_check'):
            self.scheduler.remove_job('daily_reminder_check')
        
        # Add new job
        self.scheduler.add_job(
            func=self.check_and_send_reminders,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='daily_reminder_check',
            name='Daily Feeding Reminder Check',
            replace_existing=True
        )
        logger.info(f"Daily reminder check scheduled for {check_time}")
    
    def check_and_send_reminders(self):
        """Check for due feedings and send notifications"""
        from reptile_tracker_db import ReptileDatabase
        
        try:
            db = ReptileDatabase(self.db_path)
            
            # Get notification settings
            settings = db.get_notification_settings()
            if not settings:
                logger.info("No notification settings configured")
                return
            
            # Get overdue and upcoming feedings
            overdue = db.get_overdue_feedings()
            upcoming = db.get_upcoming_feedings(days_ahead=1)
            
            # Determine what to notify about
            if settings.get('notify_overdue_only'):
                to_notify = overdue
                logger.info(f"Checking {len(overdue)} overdue feedings")
            else:
                to_notify = overdue + upcoming
                logger.info(f"Checking {len(overdue)} overdue and {len(upcoming)} upcoming feedings")
            
            if not to_notify:
                logger.info("No feedings require notification")
                return
            
            # Send notifications
            for feeding in to_notify:
                self.send_notification(feeding, settings, is_overdue=(feeding in overdue))
            
            logger.info(f"Sent {len(to_notify)} feeding reminders")
            
        except Exception as e:
            logger.error(f"Error checking reminders: {e}")
    
    def send_notification(self, feeding, settings, is_overdue=False):
        """
        Send notification for a feeding reminder
        Args:
            feeding: Feeding reminder dict
            settings: Notification settings dict
            is_overdue: Whether feeding is overdue
        """
        reptile_name = feeding.get('reptile_name', 'Unknown')
        food_type = feeding.get('food_type', 'food')
        food_size = feeding.get('food_size', '')
        next_date = feeding.get('next_feeding_date', '')
        
        # Format food item
        food_item = f"{food_size} {food_type}" if food_size else food_type
        
        # Create message
        if is_overdue:
            subject = f"🚨 Overdue Feeding: {reptile_name}"
            message = f"{reptile_name} was due for feeding on {next_date}. Time to feed {food_item}!"
        else:
            subject = f"🦎 Feeding Reminder: {reptile_name}"
            message = f"{reptile_name} is due for feeding today. Feed {food_item}."
        
        # Send email if enabled
        if settings.get('email_enabled') and settings.get('email'):
            self.send_email(settings['email'], subject, message)
        
        # Send SMS if enabled
        if settings.get('sms_enabled') and settings.get('phone'):
            self.send_sms(settings['phone'], message)
        
        # Send push notification (to all registered devices)
        self.send_push_notification(subject, message, feeding)
    
    def send_email(self, to_email, subject, message):
        """Send email notification"""
        try:
            # TODO: Implement email sending with SMTP or service like SendGrid
            logger.info(f"Email notification: {to_email} - {subject}")
            # Placeholder for actual email implementation
            pass
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    
    def send_sms(self, phone, message):
        """Send SMS notification"""
        try:
            # TODO: Implement SMS sending with service like Twilio
            logger.info(f"SMS notification: {phone} - {message}")
            # Placeholder for actual SMS implementation
            pass
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
    
    def send_push_notification(self, title, body, feeding_data):
        """Send push notification to all registered devices"""
        try:
            from reptile_tracker_db import ReptileDatabase
            
            db = ReptileDatabase(self.db_path)
            
            # Get all registered push subscriptions
            subscriptions = db.get_push_subscriptions()
            
            if not subscriptions:
                logger.info("No push subscriptions registered")
                return
            
            # Send to each subscription
            from pywebpush import webpush, WebPushException
            import json
            
            notification_data = {
                'title': title,
                'body': body,
                'icon': '/static/icon-192.png',
                'badge': '/static/icon-192.png',
                'data': {
                    'url': f"/reptile/{feeding_data.get('reptile_id', '')}",
                    'reptile_id': feeding_data.get('reptile_id'),
                    'feeding_id': feeding_data.get('id')
                }
            }
            
            sent_count = 0
            failed_count = 0
            
            for sub in subscriptions:
                try:
                    webpush(
                        subscription_info=json.loads(sub['subscription_json']),
                        data=json.dumps(notification_data),
                        vapid_private_key=sub.get('vapid_private_key'),
                        vapid_claims={
                            "sub": "mailto:reptiletracker@example.com"
                        }
                    )
                    sent_count += 1
                except WebPushException as e:
                    logger.error(f"Failed to send push to device {sub['id']}: {e}")
                    failed_count += 1
                    
                    # Remove invalid subscriptions
                    if e.response and e.response.status_code in [404, 410]:
                        db.remove_push_subscription(sub['id'])
                        logger.info(f"Removed invalid subscription {sub['id']}")
            
            logger.info(f"Push notifications sent: {sent_count}, failed: {failed_count}")
            
        except Exception as e:
            logger.error(f"Failed to send push notifications: {e}")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("Reminder scheduler stopped")


# Global scheduler instance
_scheduler = None


def init_scheduler(app, db_path):
    """Initialize the scheduler with Flask app"""
    global _scheduler
    
    if _scheduler is None:
        _scheduler = ReminderScheduler(db_path)
        
        # Set up daily check at configured time
        from reptile_tracker_db import ReptileDatabase
        db = ReptileDatabase(db_path)
        settings = db.get_notification_settings()
        
        check_time = '09:00'  # Default
        if settings and settings.get('reminder_time'):
            check_time = settings['reminder_time']
        
        _scheduler.setup_daily_check(check_time)
        
        # Register shutdown handler
        import atexit
        atexit.register(lambda: _scheduler.shutdown())
        
        logger.info(f"Scheduler initialized with check time: {check_time}")
    
    return _scheduler


def get_scheduler():
    """Get the global scheduler instance"""
    return _scheduler

# Made with Bob
