"""
Notification Service for Reptile Tracker
Handles email, SMS, and push notifications for feeding reminders
"""

import os
import smtplib
import json
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

# Web Push for push notifications
try:
    from pywebpush import webpush, WebPushException
    from py_vapid import Vapid
    WEBPUSH_AVAILABLE = True
except ImportError:
    WEBPUSH_AVAILABLE = False
    print("[WARNING] pywebpush not available. Push notifications will not work.")


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
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
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
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=to_phone
            )
            print(f"[INFO] SMS sent to {to_phone}, SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send SMS: {e}")
            return False
    
    def send_feeding_reminder(self, reptile_name: str, days_overdue: int, 
                            email: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, bool]:
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
                           email: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, int]:
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


def check_and_send_reminders(db_instance, email: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, int]:
    """
    Check for overdue feedings and send reminders
    This function can be called by a scheduled job
    """
    overdue = db_instance.get_overdue_feedings()
    
    if not overdue:
        print("[INFO] No overdue feedings found")
        return {'email_sent': 0, 'sms_sent': 0, 'total': 0}
    
    print(f"[INFO] Found {len(overdue)} overdue feeding(s)")
    return notification_service.send_batch_reminders(overdue, email, phone)


# ==================== PUSH NOTIFICATION FUNCTIONS ====================

def get_or_create_vapid_keys():
    """Get existing VAPID keys or generate new ones"""
    private_key = os.environ.get('VAPID_PRIVATE_KEY')
    public_key = os.environ.get('VAPID_PUBLIC_KEY')
    
    if private_key and public_key:
        return {
            'private_key': private_key,
            'public_key': public_key
        }
    
    # Generate new VAPID keys if not found
    if not WEBPUSH_AVAILABLE:
        print("[ERROR] Cannot generate VAPID keys - pywebpush not installed")
        return None
    
    try:
        vapid = Vapid()
        vapid.generate_keys()
        
        # Get keys using the correct py-vapid methods
        private_key = vapid.private_pem().decode('utf-8').strip()
        
        # Use save_public_key to get the base64 encoded public key
        import base64
        from io import BytesIO
        public_key_file = BytesIO()
        vapid.save_public_key(public_key_file)
        public_key_file.seek(0)
        public_key_pem = public_key_file.read()
        
        # Extract the base64 part from PEM format and make it URL-safe
        public_key_b64 = public_key_pem.decode('utf-8').split('\n')[1:-2]
        public_key = ''.join(public_key_b64).replace('+', '-').replace('/', '_').rstrip('=')
        
        print("[INFO] Generated new VAPID keys")
        print(f"[INFO] Add these to your environment variables:")
        print(f"VAPID_PRIVATE_KEY={private_key}")
        print(f"VAPID_PUBLIC_KEY={public_key}")
        
        return {
            'private_key': private_key,
            'public_key': public_key
        }
    except Exception as e:
        print(f"[ERROR] Failed to generate VAPID keys: {e}")
        import traceback
        traceback.print_exc()
        # Return a fallback for development
        print("[WARNING] Using fallback keys for development only!")
        return {
            'private_key': '',
            'public_key': 'BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U'
        }


def send_push_notification(subscription_info: Dict, title: str, body: str, url: str = '/') -> bool:
    """Send a push notification to a specific subscription"""
    if not WEBPUSH_AVAILABLE:
        print("[ERROR] Push notifications not available - pywebpush not installed")
        return False
    
    vapid_keys = get_or_create_vapid_keys()
    if not vapid_keys:
        print("[ERROR] VAPID keys not available")
        return False
    
    try:
        # Parse subscription if it's a JSON string
        if isinstance(subscription_info, str):
            subscription_info = json.loads(subscription_info)
        
        # Extract subscription data
        if 'subscription' in subscription_info:
            subscription_data = subscription_info['subscription']
        elif 'subscription_json' in subscription_info:
            subscription_data = json.loads(subscription_info['subscription_json'])
        else:
            subscription_data = subscription_info
        
        # Prepare notification payload
        notification_data = {
            'title': title,
            'body': body,
            'url': url,
            'icon': '/static/icon-192.png',
            'badge': '/static/icon-192.png'
        }
        
        # Send push notification
        webpush(
            subscription_info=subscription_data,
            data=json.dumps(notification_data),
            vapid_private_key=vapid_keys['private_key'],
            vapid_claims={
                "sub": "mailto:reptiletracker@example.com"
            }
        )
        
        print(f"[INFO] Push notification sent: {title}")
        return True
        
    except WebPushException as e:
        print(f"[ERROR] WebPush failed: {e}")
        # If subscription is invalid (410 Gone), it should be removed from database
        if e.response and e.response.status_code == 410:
            print("[INFO] Subscription expired (410 Gone) - should be removed")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to send push notification: {e}")
        return False


def send_push_to_user(db_instance, user_id: int, title: str, body: str, url: str = '/') -> Dict[str, int]:
    """Send push notification to all devices registered for a user"""
    results = {'success_count': 0, 'failed_count': 0, 'expired_subscriptions': []}
    
    try:
        subscriptions = db_instance.get_push_subscriptions(user_id=user_id)
        
        for sub in subscriptions:
            success = send_push_notification(sub, title, body, url)
            if success:
                results['success_count'] += 1
            else:
                results['failed_count'] += 1
                # Track potentially expired subscriptions
                results['expired_subscriptions'].append(sub.get('id'))
        
        return results
        
    except Exception as e:
        print(f"[ERROR] Failed to send push notifications to user {user_id}: {e}")
        return results

# Made with Bob
