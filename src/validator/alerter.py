from abc import ABC, abstractmethod
from typing import List, Dict
from .logger import logger

class AlertChannel(ABC):
    @abstractmethod
    def send_alert(self, subject: str, message: str, details: Dict = None):
        pass

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
import os
import base64

class EmailChannel(AlertChannel):
    def __init__(self, smtp_server="smtp.gmail.com", port=587, use_tls=True):
        self.smtp_server = os.getenv("SMTP_SERVER", smtp_server)
        self.port = int(os.getenv("SMTP_PORT", port))
        self.use_tls = use_tls
        self.username = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASSWORD")
        # Recipients can be list or single string
        env_recipient = os.getenv("ALERT_EMAIL_RECIPIENT", "admin@example.com")
        self.recipients = [env_recipient] if env_recipient else []

    def send_alert(self, subject: str, message: str, details: Dict = None):
        logger.info(f"[EMAIL] Preparing to send email: {subject}")
        
        if not self.username or not self.password:
            logger.warning("[EMAIL] SMTP credentials not found. Skipping.")
            logger.info(f"[EMAIL MOCK] To: {self.recipients}\nSubject: {subject}\nBody: {message}")
            return
        
        # Ensure recipients is a list
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
                logger.error(f"[EMAIL] Failed to send email to {recipient}: {e}")

class ServiceNowChannel(AlertChannel):
    def __init__(self, instance_url=None, username=None, password=None):
        # Default to env vars if not provided
        self.instance_url = instance_url or os.getenv("SNOW_INSTANCE_URL")
        self.username = username or os.getenv("SNOW_USER")
        self.password = password or os.getenv("SNOW_PASSWORD")
        
    def send_alert(self, subject: str, message: str, details: Dict = None):
        logger.info(f"[SERVICENOW] Preparing to create incident: {subject}")
        
        if not self.instance_url or not self.username or not self.password:
            logger.warning("[SERVICENOW] Credentials missing (SNOW_INSTANCE_URL, SNOW_USER, SNOW_PASSWORD). Skipping API call.")
            return

        # ServiceNow Table API URL
        # URL format: https://{instance}.service-now.com/api/now/table/incident
        api_url = f"{self.instance_url.rstrip('/')}/api/now/table/incident"
        
        payload = {
            "short_description": subject,
            "description": message,
            "category": "Software",
            "priority": "2" # High
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            # Using httpx for HTTP requests
            response = httpx.post(
                api_url, 
                auth=(self.username, self.password), 
                headers=headers, 
                json=payload,
                timeout=10.0
            )
            
            if response.status_code == 201:
                data = response.json()
                incident_number = data.get("result", {}).get("number", "Unknown")
                logger.info(f"[SERVICENOW] Incident created successfully: {incident_number}")
            else:
                logger.error(f"[SERVICENOW] Failed to create incident. Status: {response.status_code}, Body: {response.text}")
                
        except Exception as e:
            logger.error(f"[SERVICENOW] Error connecting to ServiceNow: {e}")

class AlertManager:
    def __init__(self):
        self.channels: List[AlertChannel] = []
        # Default channels (using env vars still works as fallback)
        self.register_channel(EmailChannel())
        # self.register_channel(ServiceNowChannel())

    def register_channel(self, channel: AlertChannel):
        self.channels.append(channel)
        
    def configure(self, config: Dict):
        """Re-initialize channels with provided config dict"""
        self.channels = [] # Reset channels
        
        # Email Config
        smtp_conf = config.get("smtp_config", {})
        recipients = config.get("email_recipients", []) # List[str]
        
        if smtp_conf or recipients:
             # Normalize recipients to single string for env var compat calling style, 
             # OR update EmailChannel to handle list. 
             # For minimal change, let's keep env var compat in mind, but prefer config.
             
             # Create args for EmailChannel
             server = smtp_conf.get("server", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
             port = smtp_conf.get("port", int(os.getenv("SMTP_PORT", 587)))
             user = smtp_conf.get("sender_email", os.getenv("SMTP_USER"))
             password = smtp_conf.get("sender_password", os.getenv("SMTP_PASSWORD"))
             
             # Recipient handling - Updated EmailChannel to support list or overriding
             channel = EmailChannel(smtp_server=server, port=port)
             channel.username = user
             channel.password = password
             channel.recipients = recipients if recipients else [os.getenv("ALERT_EMAIL_RECIPIENT", "admin@example.com")]
             
             self.register_channel(channel)
             
        # ServiceNow Config
        snow_conf = config.get("servicenow", {})
        if snow_conf:
            instance = snow_conf.get("instance_url", os.getenv("SNOW_INSTANCE_URL"))
            user = snow_conf.get("username", os.getenv("SNOW_USER"))
            password = snow_conf.get("password", os.getenv("SNOW_PASSWORD"))
            
            channel = ServiceNowChannel(instance_url=instance, username=user, password=password)
            self.register_channel(channel)
        elif os.getenv("SNOW_INSTANCE_URL"):
            # Fallback to env var if config not present but env var is
            self.register_channel(ServiceNowChannel())

    def trigger_alert(self, filename: str, rule_name: str, failures: List[Dict]):
        if not failures:
            return

        subject = f"File Validation Alert: {os.path.basename(filename)}"
        message = f"The file '{os.path.basename(filename)}' has failed validation.\n"
        message += f"Total Errors Found: {len(failures)}\n\n"
        message += "Sample Errors:\n"
        
        for fail in failures[:10]: # Limit to first 10
            row = fail.get('row', 'N/A')
            msg = fail.get('message', 'Unknown issue')
            message += f"- Row {row}: {msg}\n"
            
        if len(failures) > 10:
            message += f"\n...and {len(failures) - 10} more errors."
            
        message += "\nPlease review and correct the file."

        details = {"filename": filename, "error_count": len(failures), "sample_errors": failures[:5]}

        for channel in self.channels:
            channel.send_alert(subject, message, details)
