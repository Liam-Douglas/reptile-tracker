"""
Notification Service for Reptile Tracker
Handles email and SMS notifications for feeding reminders
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional

# Twilio for SMS (optional)
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


class NotificationService:
    """Service for sending email and SMS notifications"""
    
    def __init__(self):
        # Email configuration (using environment variables)
        self.email_enabled = os.environ.get('SMTP_ENABLED', 'false').lower() == 'true'
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', self.smtp_username)
        
        # SMS configuration (Twilio)
        self.sms_enabled = os.environ.get('TWILIO_ENABLED', 'false').lower() == 'true'
        self.twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
        self.twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER', '')
        
        # Initialize Twilio client if available
        self.twilio_client = None
        if self.sms_enabled and TWILIO_AVAILABLE and self.twilio_account_sid and self.twilio_auth_token:
            try:
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
            except Exception as e:
                print(f"[WARNING] Failed to initialize Twilio client: {e}")
                self.sms_enabled = False
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send an email notification"""
        if not self.email_enabled:
            print("[INFO] Email notifications are disabled")
            return False
        
        if not self.smtp_username or not self.smtp_password:
            print("[WARNING] SMTP credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text and HTML parts
            msg.attach(MIMEText(body, 'plain'))
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"[INFO] Email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
            return False
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """Send an SMS notification via Twilio"""
        if not self.sms_enabled:
            print("[INFO] SMS notifications are disabled")
            return False
        
        if not self.twilio_client:
            print("[WARNING] Twilio client not initialized")
            return False
        
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=to_phone
            )
            print(f"[INFO] SMS sent to {to_phone}, SID: {message.sid}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send SMS: {e}")
            return False
    
    def send_feeding_reminder(self, reptile_name: str, days_overdue: int, 
                            email: str = None, phone: str = None) -> Dict[str, bool]:
        """Send feeding reminder via email and/or SMS"""
        results = {'email': False, 'sms': False}
        
        # Prepare message content
        if days_overdue == 0:
            subject = f"🦎 Feeding Reminder: {reptile_name} is due for feeding today!"
            message = f"Reminder: {reptile_name} is scheduled to be fed today."
        elif days_overdue > 0:
            subject = f"🚨 Overdue Feeding: {reptile_name} is {days_overdue} day(s) overdue!"
            message = f"URGENT: {reptile_name} is {days_overdue} day(s) overdue for feeding!"
        else:
            subject = f"🦎 Upcoming Feeding: {reptile_name} due in {abs(days_overdue)} day(s)"
            message = f"Reminder: {reptile_name} will be due for feeding in {abs(days_overdue)} day(s)."
        
        # HTML email body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2c5f2d;">🦎 Reptile Tracker Feeding Reminder</h2>
            <div style="background-color: {'#ffebee' if days_overdue > 0 else '#e8f5e9'}; 
                        padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">{reptile_name}</h3>
                <p style="font-size: 16px; margin: 10px 0;">
                    {message}
                </p>
            </div>
            <p style="color: #666; font-size: 14px;">
                Log into your Reptile Tracker to record the feeding and update the schedule.
            </p>
        </body>
        </html>
        """
        
        # Send email if provided
        if email:
            results['email'] = self.send_email(email, subject, message, html_body)
        
        # Send SMS if provided
        if phone:
            sms_message = f"Reptile Tracker: {message}"
            results['sms'] = self.send_sms(phone, sms_message)
        
        return results
    
    def send_batch_reminders(self, overdue_feedings: List[Dict], 
                           email: str = None, phone: str = None) -> Dict[str, int]:
        """Send batch reminders for multiple overdue feedings"""
        results = {'email_sent': 0, 'sms_sent': 0, 'total': len(overdue_feedings)}
        
        if not overdue_feedings:
            return results
        
        # Send individual reminders for each reptile
        for feeding in overdue_feedings:
            reptile_name = feeding.get('reptile_name', 'Unknown')
            next_feeding = feeding.get('next_feeding_date')
            
            if next_feeding:
                try:
                    next_date = datetime.strptime(next_feeding, '%Y-%m-%d')
                    today = datetime.now()
                    days_overdue = (today - next_date).days
                    
                    reminder_results = self.send_feeding_reminder(
                        reptile_name, days_overdue, email, phone
                    )
                    
                    if reminder_results['email']:
                        results['email_sent'] += 1
                    if reminder_results['sms']:
                        results['sms_sent'] += 1
                        
                except Exception as e:
                    print(f"[ERROR] Failed to send reminder for {reptile_name}: {e}")
        
        return results


# Global notification service instance
notification_service = NotificationService()


def check_and_send_reminders(db, email: str = None, phone: str = None) -> Dict[str, int]:
    """
    Check for overdue feedings and send reminders
    This function can be called by a scheduled job
    """
    overdue = db.get_overdue_feedings()
    
    if not overdue:
        print("[INFO] No overdue feedings found")
        return {'email_sent': 0, 'sms_sent': 0, 'total': 0}
    
    print(f"[INFO] Found {len(overdue)} overdue feeding(s)")
    return notification_service.send_batch_reminders(overdue, email, phone)

# Made with Bob
