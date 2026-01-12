"""
Twitter Digest Service - Main Entry Point

This script orchestrates the complete Twitter digest generation process:
1. Fetch tweets from user's timeline
2. Process and analyze tweets
3. Generate email digest
4. Send via email

Usage:
    python -m nuzzel.main
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from nuzzel.twitter_client import create_twitter_client
from nuzzel.email_client import create_email_client
from nuzzel.processors.tweet_processor import process_data_for_digest
from nuzzel.generators.digest_generator import generate_email_digest
from nuzzel.utils.validation import (
    validate_time_window,
    validate_email_address,
    ValidationError
)
from nuzzel.constants import DEFAULT_TIME_WINDOW_DAYS


# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class TwitterDigestService:
    """Main service class for Twitter digest generation"""

    def __init__(self, time_window_days: int, recipient_email: str, mailjet_api_key: str, mailjet_api_secret: str, sender_email: str):
        self.time_window_days = time_window_days
        self.twitter_client = create_twitter_client()
        self.email_client = create_email_client(mailjet_api_key, mailjet_api_secret, sender_email, recipient_email)

    async def run_digest_generation(self) -> bool:
        """
        Run the complete digest generation process.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting Twitter digest generation...")

        try:
            # Step 1: Get user ID
            logger.info("Fetching user ID...")
            if hasattr(self.twitter_client, 'get_user_id_async'):
                user_id = await self.twitter_client.get_user_id_async()
            else:
                user_id = await self.twitter_client.get_user_id()
            logger.debug("Authenticated as user: %s", user_id)
        except Exception as e:
            logger.error("Failed to get user ID: %s", e, exc_info=True)
            return await self._send_error_digest(f"Failed to authenticate with Twitter API: {str(e)}")

        # Step 2: Calculate time window
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=self.time_window_days)
        logger.info("Fetching tweets from %s to %s", start_time, end_time)

        try:
            # Step 3: Fetch timeline data
            logger.info("Fetching timeline data...")
            if hasattr(self.twitter_client, 'get_user_timeline_async'):
                timeline_data = await self.twitter_client.get_user_timeline_async(start_time)
            else:
                timeline_data = await self.twitter_client.get_user_timeline(start_time, max_pages=3)
        except Exception as e:
            logger.error("Failed to fetch timeline data: %s", e, exc_info=True)
            return await self._send_error_digest(f"Failed to fetch tweets from timeline: {str(e)}")

        tweet_count = len(timeline_data.get('data', []))
        logger.info("Fetched %s tweets", tweet_count)

        if tweet_count == 0:
            logger.warning("No tweets found in time window")
            return await self._send_empty_digest("No tweets found in the specified time window")

        # Step 4: Fetch user engagement history
        logger.info("Fetching user engagement history...")
        if hasattr(self.twitter_client, 'get_user_liked_tweets_async'):
            liked_tweets = await self.twitter_client.get_user_liked_tweets_async(max_results=10)
        else:
            liked_tweets = await self.twitter_client.get_user_liked_tweets(max_results=10)

        if hasattr(self.twitter_client, 'get_user_tweets_async'):
            posted_tweets = await self.twitter_client.get_user_tweets_async(max_results=10)
        else:
            posted_tweets = await self.twitter_client.get_user_tweets(max_results=10)

        # Step 6: Process tweets
        logger.info("Processing tweets...")
        processed_data = process_data_for_digest(
            timeline_data, liked_tweets, posted_tweets
        )

        # Step 7: Generate digest
        logger.info("Generating email digest...")
        digest_result = generate_email_digest(processed_data, self.time_window_days)

        # Step 8: Send email
        logger.info("Sending email digest...")
        success = self.email_client.send_email(
            subject=digest_result['subject'],
            html_content=digest_result['html_content']
        )

        if success:
            logger.info("Digest sent successfully!")
            return True
        else:
            logger.error("Failed to send digest email")
            return False



    async def _send_empty_digest(self, message: str) -> bool:
        """
        Send a digest indicating no tweets were found.

        Args:
            message: Message to include

        Returns:
            True if email sent successfully
        """
        subject = f"Twitter Digest: No Activity ({datetime.now().strftime('%B %d, %Y')})"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1>Your Twitter Digest</h1>
            <p>{message}</p>
            <p>This could mean:</p>
            <ul>
                <li>No new tweets from accounts you follow in the last {self.time_window_days} days</li>
                <li>API rate limiting or connectivity issues</li>
                <li>Configuration issues</li>
            </ul>
            <p>Please check the logs for more details.</p>
        </body>
        </html>
        """

        return self.email_client.send_email(
            subject=subject,
            html_content=html_content
        )

    async def _send_error_digest(self, error_msg: str) -> bool:
        """
        Send an error digest when processing fails.

        Args:
            error_msg: Error message

        Returns:
            True if email sent successfully
        """
        subject = f"Twitter Digest: Error ({datetime.now().strftime('%B %d, %Y')})"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1>Twitter Digest - Error</h1>
            <p>There was an error generating your Twitter digest:</p>
            <p><strong>{error_msg}</strong></p>
            <p>Please check the application logs for more details.</p>
        </body>
        </html>
        """

        return self.email_client.send_email(
            subject=subject,
            html_content=html_content
        )

async def main() -> int:
    """Main entry point"""
    # Check required environment variables
    try:
        recipient_email = validate_email_address(os.getenv("RECIPIENT_EMAIL", ""))
    except ValidationError:
        return 1

    try:
        sender_email = validate_email_address(os.getenv("SENDER_EMAIL", ""))
    except ValidationError:
        return 1

    # Get and validate time window
    try:
        time_window_days = validate_time_window(DEFAULT_TIME_WINDOW_DAYS)
    except ValidationError as e:
        logger.error("Invalid time window: %s. Using default time window of 1 day.", e, exc_info=True)
        time_window_days = 1
        return 1

    mailjet_api_key = os.getenv('MAILJET_API_KEY')
    mailjet_api_secret = os.getenv('MAILJET_API_SECRET')
    if not mailjet_api_key or not mailjet_api_secret:
        logger.error("MAILJET_API_KEY and MAILJET_API_SECRET must be set")
        return 1

    # Initialize and run service
    service = TwitterDigestService(
        time_window_days=time_window_days,
        recipient_email=recipient_email,
        mailjet_api_key=mailjet_api_key,
        mailjet_api_secret=mailjet_api_secret,
        sender_email=sender_email
    )
    try:
        success = await service.run_digest_generation()
        return 0 if success else 1
    finally:
        # Cleanup: close browser client if it has a close method
        if hasattr(service.twitter_client, 'close'):
            logger.info("Closing browser client...")
            await service.twitter_client.close()


if __name__ == "__main__":
    import asyncio
    exit(asyncio.run(main()))
