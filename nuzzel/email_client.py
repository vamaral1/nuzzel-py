"""
Email Client using Mailjet API

This module provides functionality to send HTML emails via Mailjet API.
"""

import logging
import os
from typing import Optional

from mailjet_rest import Client # type: ignore[import-untyped]

# Configure logging
logger = logging.getLogger(__name__)


class EmailClient:
    """Mailjet email client for sending HTML emails

    This client implements Gmail sender guidelines to improve deliverability:
    - Reply-To header via Mailjet's ReplyTo property
    - List-Unsubscribe headers for one-click unsubscribe
    - Clear, non-misleading display names
    - RFC 5322 compliant message formatting (Message-ID and Date handled automatically by Mailjet)

    Note: For best deliverability:
    - sender_email and recipient_email should ideally be different
    - Your sending domain must have SPF, DKIM, and DMARC records configured
    - Mailjet must be authenticated with your domain
    - Only send to recipients who have opted in
    """

    def __init__(self, api_key: Optional[str], api_secret: Optional[str], sender_email: str, recipient_email: str):

        if not api_key or not api_secret:
            raise ValueError("Mailjet API credentials required")
        if not sender_email:
            raise ValueError("Sender email is required")
        if not recipient_email:
            raise ValueError("Recipient email is required")

        self.api_key = api_key
        self.api_secret = api_secret
        self.sender_email = sender_email
        self.recipient_email = recipient_email

        self.client = Client(auth=(self.api_key, self.api_secret), version='v3.1')

    def send_email(self,
                   subject: str,
                   html_content: str,
                   from_name: str = "Twitter Digest",
                   reply_to: Optional[str] = None,
                   unsubscribe_url: Optional[str] = None) -> bool:
        """
        Send HTML email via Mailjet with proper headers for deliverability.

        Args:
            subject: Email subject line (should be clear and not misleading)
            html_content: HTML content of the email
            from_name: Sender display name (should clearly identify sender, no misleading content)
            reply_to: Reply-To email address (defaults to sender_email if not provided)
            unsubscribe_url: URL for one-click unsubscribe (recommended for bulk senders)

        Returns:
            True if email sent successfully, False otherwise
        """
        # Set Reply-To to sender_email if not provided
        if reply_to is None:
            reply_to = self.sender_email

        # Build message data
        # Note: Mailjet automatically handles Message-ID and Date headers
        message_data = {
            "From": {
                "Email": self.sender_email,
                "Name": from_name
            },
            "To": [
                {
                    "Email": self.recipient_email
                }
            ],
            "Subject": subject,
            "HTMLPart": html_content,
            "ReplyTo": {
                "Email": reply_to
            },
            "CustomID": "TwitterDigest",
            "TrackClicks": "disabled"  # Disable click tracking to prevent mjt.lu redirect URLs
        }

        # Add List-Unsubscribe headers for better deliverability (one-click unsubscribe)
        # This is required for senders of 5,000+ messages/day, but recommended for all
        # These can be set via Headers collection
        if unsubscribe_url:
            message_data["Headers"] = {
                "List-Unsubscribe": f"<{unsubscribe_url}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"
            }

        data = {
            'Messages': [message_data]
        }

        try:
            result = self.client.send.create(data=data)
        except Exception as e:
            logger.error("Error sending email: %s", e, exc_info=True)
            return False

        # Check response
        if result.status_code == 200:
            response_data = result.json()
            if 'Messages' in response_data:
                message = response_data['Messages'][0]
                if message.get('Status') == 'success':
                    logger.info("Email sent successfully to %s", self.recipient_email)
                    return True
                else:
                    logger.error("Email send failed: %s", message)
                    return False
            else:
                logger.error("Unexpected response format: %s", response_data)
                return False
        else:
            logger.error("Mailjet API error: %d - %s", result.status_code, result.text)
            return False


    def send_test_email(self,
                       subject: str = "Twitter Digest Test",
                       html_content: str = "<h1>Test Email</h1><p>This is a test email from Twitter Digest.</p>") -> bool:
        """
        Send a test email to verify configuration.

        Args:
            subject: Test subject
            html_content: Test HTML content

        Returns:
            True if test email sent successfully
        """
        logger.info("Sending test email...")
        return self.send_email(subject, html_content)


class MockEmailClient(EmailClient):
    """Mock email client for testing that doesn't send actual emails"""

    def __init__(self, api_key: str = "mock_key", api_secret: str = "mock_secret", sender_email: str = "mock@example.com", recipient_email: str = "mock@example.com"):
        # Don't call super().__init__ since we don't need real Mailjet setup
        self.api_key = api_key
        self.api_secret = api_secret
        self.sender_email = sender_email
        self.recipient_email = recipient_email

    def send_email(self,
                   subject: str,
                   html_content: str,
                   from_name: str = "Twitter Digest",
                   reply_to: Optional[str] = None,
                   unsubscribe_url: Optional[str] = None) -> bool:
        """
        Mock email sending - always succeeds and logs the action.

        Args:
            subject: Email subject line
            html_content: HTML content of the email
            from_name: Sender display name
            reply_to: Reply-To email address (ignored in mock)
            unsubscribe_url: Unsubscribe URL (ignored in mock)

        Returns:
            True (mock always succeeds)
        """
        logger.info("MOCK EMAIL: Would send email to %s with subject '%s' (not actually sent)",
            self.recipient_email, subject)
        return True

    def send_test_email(
        self,
        subject: str = "Twitter Digest Test",
        html_content: str = "<h1>Test Email</h1><p>This is a test email from Twitter Digest.</p>"
    ) -> bool:
        """
        Mock test email sending - always succeeds.

        Args:
            subject: Test subject
            html_content: Test HTML content

        Returns:
            True (mock always succeeds)
        """
        logger.info("MOCK TEST EMAIL: Would send test email to %s (not actually sent)", self.recipient_email)
        return True


def create_email_client(mailjet_api_key: Optional[str] = None,
                        mailjet_api_secret: Optional[str] = None,
                        sender_email: str = "",
                        recipient_email: str = "") -> EmailClient:
    """
    Factory function to create appropriate email client based on environment.

    Note: For best deliverability, sender_email and recipient_email should ideally be different.
    Using the same email for both sender and recipient may cause emails to be flagged as spam
    by email providers, as it can appear suspicious or like self-mailing behavior.

    Args:
        mailjet_api_key: Mailjet API key
        mailjet_api_secret: Mailjet API secret
        sender_email: Sender email address
        recipient_email: Recipient email address

    Returns:
        EmailClient instance (real or mock)
    """
    use_mock = os.getenv("USE_MOCK", "false").lower() == "true"

    if use_mock:
        logger.info("Using mock email client")
        return MockEmailClient(
            api_key=mailjet_api_key or "mock_key",
            api_secret=mailjet_api_secret or "mock_secret",
            sender_email=sender_email or "mock@example.com",
            recipient_email=recipient_email or "mock@example.com"
        )
    else:
        logger.info("Using real Mailjet email client")
        return EmailClient(
            api_key=mailjet_api_key,
            api_secret=mailjet_api_secret,
            sender_email=sender_email,
            recipient_email=recipient_email
        )
