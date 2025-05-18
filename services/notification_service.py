"""
Notification service for the surgery scheduling application.

This module provides a service for sending notifications to users via email,
SMS, or other channels. It uses a singleton pattern to ensure that only one
instance of the service is created.
"""

import os
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import threading
import queue
import time

from services.exceptions import NotificationError, ConfigurationError
from services.logger_config import logger

class NotificationType(Enum):
    """Types of notifications that can be sent."""
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    """Priority levels for notifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(Enum):
    """Status of a notification."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


class Notification:
    """
    Represents a notification to be sent.

    Attributes:
        recipient: The recipient of the notification.
        subject: The subject of the notification.
        body: The body of the notification.
        notification_type: The type of notification (email, SMS, etc.).
        priority: The priority of the notification.
        status: The status of the notification.
        created_at: When the notification was created.
        sent_at: When the notification was sent.
        retry_count: Number of retry attempts.
    """

    def __init__(
        self,
        recipient: str,
        subject: str,
        body: str,
        notification_type: NotificationType = NotificationType.EMAIL,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.notification_type = notification_type
        self.priority = priority
        self.metadata = metadata or {}
        self.status = NotificationStatus.PENDING
        self.created_at = datetime.now()
        self.sent_at = None
        self.retry_count = 0
        self.error = None


class SingletonMeta(type):
    """Metaclass for implementing the Singleton pattern."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Ensure only one instance of the class is created.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The singleton instance of the class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class NotificationService(metaclass=SingletonMeta):
    """
    Service for sending notifications to users.

    This service supports sending notifications via email, SMS, or other channels.
    It uses a background thread to process notifications asynchronously.
    """

    def __init__(self):
        """Initialize the notification service."""
        # Email setup from environment variables for enhanced security
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM', self.smtp_user)

        # SMS setup (placeholder for future implementation)
        self.sms_api_key = os.getenv('SMS_API_KEY')
        self.sms_api_secret = os.getenv('SMS_API_SECRET')
        self.sms_from = os.getenv('SMS_FROM')

        # Queue for asynchronous processing
        self.queue = queue.PriorityQueue()
        self.queue_thread = None
        self.queue_running = False

        # Start the queue processing thread
        self.start_queue_processing()

    def start_queue_processing(self):
        """Start the background thread for processing notifications."""
        if self.queue_thread is None or not self.queue_thread.is_alive():
            self.queue_running = True
            self.queue_thread = threading.Thread(
                target=self._process_queue,
                daemon=True
            )
            self.queue_thread.start()
            logger.info("Notification queue processing started")

    def stop_queue_processing(self):
        """Stop the background thread for processing notifications."""
        self.queue_running = False
        if self.queue_thread and self.queue_thread.is_alive():
            self.queue_thread.join(timeout=5.0)
            logger.info("Notification queue processing stopped")

    def _process_queue(self):
        """Process notifications in the queue."""
        while self.queue_running:
            try:
                # Get the next notification from the queue
                priority, _, notification = self.queue.get(block=True, timeout=1.0)

                # Process the notification
                try:
                    self._send_notification(notification)
                    notification.status = NotificationStatus.SENT
                    notification.sent_at = datetime.now()
                    logger.info(
                        f"Notification sent to {notification.recipient} "
                        f"with subject '{notification.subject}'"
                    )
                except Exception as e:
                    notification.status = NotificationStatus.FAILED
                    notification.error = str(e)
                    logger.error(
                        f"Failed to send notification to {notification.recipient}: {e}"
                    )

                    # Retry if needed
                    if notification.retry_count < 3:
                        notification.retry_count += 1
                        notification.status = NotificationStatus.RETRYING
                        # Put back in queue with lower priority
                        self.queue.put((
                            priority + notification.retry_count,
                            time.time(),
                            notification
                        ))
                        logger.info(
                            f"Retrying notification to {notification.recipient} "
                            f"(attempt {notification.retry_count})"
                        )

                # Mark the task as done
                self.queue.task_done()

            except queue.Empty:
                # No notifications in the queue, sleep for a bit
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in notification queue processing: {e}")
                time.sleep(1.0)  # Sleep to avoid tight loop on error

    def _send_notification(self, notification: Notification):
        """
        Send a notification.

        Args:
            notification: The notification to send.

        Raises:
            NotificationError: If the notification cannot be sent.
            ConfigurationError: If the notification service is not configured.
        """
        if notification.notification_type == NotificationType.EMAIL:
            self._send_email(notification)
        elif notification.notification_type == NotificationType.SMS:
            self._send_sms(notification)
        elif notification.notification_type == NotificationType.IN_APP:
            self._send_in_app(notification)
        else:
            raise NotificationError(f"Unsupported notification type: {notification.notification_type}")

    def _send_email(self, notification: Notification):
        """
        Send an email notification.

        Args:
            notification: The notification to send.

        Raises:
            NotificationError: If the email cannot be sent.
            ConfigurationError: If the email service is not configured.
        """
        # Check if email configuration is available
        if not all([self.smtp_server, self.smtp_port, self.smtp_user, self.smtp_password]):
            raise ConfigurationError("Email configuration is incomplete")

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = notification.recipient
            msg['Subject'] = notification.subject

            # Attach body
            msg.attach(MIMEText(notification.body, 'html'))

            # Create secure connection and send message
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

        except Exception as e:
            raise NotificationError("Failed to send email", original_exception=e)

    def _send_sms(self, notification: Notification):
        """
        Send an SMS notification.

        Args:
            notification: The notification to send.

        Raises:
            NotificationError: If the SMS cannot be sent.
            ConfigurationError: If the SMS service is not configured.
        """
        # Check if SMS configuration is available
        if not all([self.sms_api_key, self.sms_api_secret, self.sms_from]):
            raise ConfigurationError("SMS configuration is incomplete")

        # Placeholder for SMS implementation
        # This would typically use a third-party SMS service API
        logger.info(f"SMS would be sent to {notification.recipient}: {notification.body}")

        # For now, just simulate success
        time.sleep(0.1)

    def _send_in_app(self, notification: Notification):
        """
        Send an in-app notification.

        Args:
            notification: The notification to send.

        Raises:
            NotificationError: If the in-app notification cannot be sent.
        """
        # Placeholder for in-app notification implementation
        # This would typically store the notification in the database
        logger.info(f"In-app notification for {notification.recipient}: {notification.subject}")

        # For now, just simulate success
        time.sleep(0.1)

    def send_notification(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        notification_type: Union[NotificationType, str] = NotificationType.EMAIL,
        priority: Union[NotificationPriority, str] = NotificationPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        async_send: bool = True
    ):
        """
        Send a notification.

        Args:
            recipient_email: The email address of the recipient.
            subject: The subject of the notification.
            body: The body of the notification.
            notification_type: The type of notification (email, SMS, etc.).
            priority: The priority of the notification.
            metadata: Additional metadata for the notification.
            async_send: Whether to send the notification asynchronously.

        Returns:
            The notification object.

        Raises:
            NotificationError: If the notification cannot be sent.
        """
        # Convert string types to enum values if needed
        if isinstance(notification_type, str):
            notification_type = NotificationType(notification_type)

        if isinstance(priority, str):
            priority = NotificationPriority(priority)

        # Create notification
        notification = Notification(
            recipient=recipient_email,
            subject=subject,
            body=body,
            notification_type=notification_type,
            priority=priority,
            metadata=metadata
        )

        # Send notification
        if async_send:
            # Add to queue for asynchronous processing
            # Priority queue items are (priority, timestamp, item)
            # Lower priority number = higher priority
            priority_value = {
                NotificationPriority.URGENT: 0,
                NotificationPriority.HIGH: 1,
                NotificationPriority.MEDIUM: 2,
                NotificationPriority.LOW: 3
            }[priority]

            self.queue.put((priority_value, time.time(), notification))
            logger.debug(
                f"Queued {notification_type.value} notification to {recipient_email} "
                f"with priority {priority.value}"
            )
        else:
            # Send immediately
            try:
                self._send_notification(notification)
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now()
                logger.info(
                    f"Sent {notification_type.value} notification to {recipient_email} "
                    f"with subject '{subject}'"
                )
            except Exception as e:
                notification.status = NotificationStatus.FAILED
                notification.error = str(e)
                logger.error(f"Failed to send notification to {recipient_email}: {e}")
                raise NotificationError("Failed to send notification", original_exception=e)

        return notification


# Singleton instance for global access
notification_service = NotificationService()
