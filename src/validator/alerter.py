"""
Alert Manager
-------------
Handles notifications and incident management integration.
Supports:
1. Email (SMTP) - Sends alerts to admins.
2. ServiceNow - Creates Incident tickets via REST API.

Design Pattern: Strategy Pattern (AlertChannel interface).
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from .logger import logger
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
import os
import base64

# --- Abstract Base Strategy ---
class AlertChannel(ABC):
    @abstractmethod
    def send_alert(self, subject: str, message: str, details: Dict = None):
        """Send an alert through the specific channel implementation."""
        pass

# --- Email Strategy ---
class EmailChannel(AlertChannel):
    """Sends alerts via SMTP."""
    
    def __init__(self, smtp_server="smtp.gmail.com", port=587, use_tls=True):
        self.smtp_server = os.getenv("SMTP_SERVER", smtp_server)
        self.port = int(os.getenv("SMTP_PORT", port))
        self.use_tls = use_tls
        self.username = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASSWORD")
        # Recipients loaded from Config or Env
        self.recipients = []

    def send_alert(self, subject: str, message: str, details: Dict = None):
        logger.info(f"[EMAIL] Preparing to send email: {subject}")
        
        if not self.username or not self.password:
            logger.warning("[EMAIL] SMTP credentials missing. Skipping email send.")
            return
        
        # Ensure list format
        recipients_list = self.recipients if isinstance(self.recipients, list) else [self.recipients]
        
        for recipient in recipients_list:
            try:
                msg = MIMEMultipart()
                msg['From'] = self.username
                msg['To'] = recipient
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'plain'))
                
                with smtplib.SMTP(self.smtp_server, self.port) as server:
                    if self.use_tls:
                        server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(msg)
                    
                logger.info(f"[EMAIL] Sent successfully to {recipient}")
            except Exception as e:
                logger.error(f"[EMAIL] Failed to send to {recipient}: {e}")

# --- ServiceNow Strategy ---
class ServiceNowChannel(AlertChannel):
    """Creates Incidents in ServiceNow via Table API."""
    
    def __init__(self, instance_url=None, username=None, password=None):
        self.instance_url = instance_url or os.getenv("SNOW_INSTANCE_URL")
        self.username = username or os.getenv("SNOW_USER")
        self.password = password or os.getenv("SNOW_PASSWORD")
        
    def send_alert(self, subject: str, message: str, details: Dict = None):
        logger.info(f"[SERVICENOW] Preparing to create incident: {subject}")
        
        if not self.instance_url or not self.username or not self.password:
            logger.warning("[SERVICENOW] Credentials missing. Skipping.")
            return

        api_url = f"{self.instance_url.rstrip('/')}/api/now/table/incident"
        
        payload = {
            "short_description": subject,
            "description": message,
            "category": "Software",
            "priority": "2" # Medium/High Priority
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = httpx.post(
                api_url, 
                auth=(self.username, self.password), 
                headers=headers, 
                json=payload,
                timeout=10.0
            )
            
            if response.status_code == 201:
                data = response.json()
                ticket = data.get("result", {}).get("number", "Unknown")
                logger.info(f"[SERVICENOW] Incident created: {ticket}")
            else:
                logger.error(f"[SERVICENOW] Failed. HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"[SERVICENOW] Connection Exception: {e}")

# --- Coordinator ---
class AlertManager:
    """
    Manages multiple alert channels and dispatches notifications
    to all registered channels upon failure.
    """
    
    def __init__(self):
        self.channels: List[AlertChannel] = []
        # Initial registration (will be overwritten by configure())
        self.register_channel(EmailChannel())

    def register_channel(self, channel: AlertChannel):
        self.channels.append(channel)
        
    def configure(self, config: Dict):
        """
        Dynamically configures channels based on JSON config.
        Allows changing recipients or credentials without restart.
        """
        self.channels = [] # Reset
        
        # 1. Configure Email
        smtp_conf = config.get("smtp_config", {})
        recipients = config.get("email_recipients", [])
        
        if smtp_conf or recipients:
             server = smtp_conf.get("server", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
             port = smtp_conf.get("port", int(os.getenv("SMTP_PORT", 587)))
             user = smtp_conf.get("sender_email", os.getenv("SMTP_USER"))
             password = smtp_conf.get("sender_password", os.getenv("SMTP_PASSWORD"))
             
             channel = EmailChannel(smtp_server=server, port=port)
             channel.username = user
             channel.password = password
             # Fallback to env var if config recipient is empty
             channel.recipients = recipients if recipients else [os.getenv("ALERT_EMAIL_RECIPIENT", "admin@example.com")]
             
             self.register_channel(channel)
             
        # 2. Configure ServiceNow
        snow_conf = config.get("servicenow", {})
        if snow_conf:
            instance = snow_conf.get("instance_url", os.getenv("SNOW_INSTANCE_URL"))
            user = snow_conf.get("username", os.getenv("SNOW_USER"))
            password = snow_conf.get("password", os.getenv("SNOW_PASSWORD"))
            
            channel = ServiceNowChannel(instance_url=instance, username=user, password=password)
            self.register_channel(channel)

    def trigger_alert(self, filename: str, rule_name: str, failures: List[Dict]):
        """
        Constructs a formatted alert message and broadcasts it.
        """
        if not failures:
            return

        subject = f"File Validation Failure: {os.path.basename(filename)}"
        message = f"File: {os.path.basename(filename)}\n"
        message += f"Ruleset: {rule_name}\n"
        message += f"Total Errors: {len(failures)}\n\n"
        message += "--- Sample Errors ---\n"
        
        for fail in failures[:10]:
            row = fail.get('row', 'N/A')
            msg = fail.get('message', 'Unknown issue')
            message += f"Row {row}: {msg}\n"
            
        if len(failures) > 10:
            message += f"...and {len(failures) - 10} more errors."
            
        details = {"filename": filename, "error_count": len(failures)}

        for channel in self.channels:
            channel.send_alert(subject, message, details)
