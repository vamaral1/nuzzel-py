"""
Update List Membership Cache

This script fetches Twitter list metadata and membership data, caching it to avoid
API calls during daily digest generation. It uses member count comparison to
only fetch list members when membership has actually changed.

Usage:
    python -m nuzzel.update_lists

Environment Variables:
    TWITTER_BEARER_TOKEN: Twitter API bearer token (not required if USE_MOCK=true)
    USE_MOCK: Set to 'true' to use mock data from fixtures instead of real API calls
"""

import json
import csv
import logging
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

from nuzzel.twitter_client import create_twitter_client, TwitterAPIError, TwitterClient
from nuzzel.utils.rate_limit_utils import sleep_with_jitter

# Load environment variables from .env file if it exists
load_dotenv()

# Constants
DATA_DIR = Path(__file__).parent.parent / "data"
LIST_METADATA_FILE = DATA_DIR / "list_metadata.json"
LIST_MEMBERSHIPS_FILE = DATA_DIR / "list_memberships.csv"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ListMembershipUpdater:
    """Updates cached list membership data using member count optimization"""

    def __init__(self, twitter_client: TwitterClient):
        self.twitter_client = twitter_client

    def load_cached_metadata(self) -> dict:
        """Load cached list metadata from JSON file"""
        if not LIST_METADATA_FILE.exists():
            return {}

        try:
            with open(LIST_METADATA_FILE, "r", encoding="utf-8") as f:
                logger.info("Loading cached metadata from %s", LIST_METADATA_FILE)
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Could not load cached metadata: %s", e)
            return {}

    def save_metadata(self, metadata: dict):
        """Save list metadata to JSON file"""
        LIST_METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LIST_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, sort_keys=True)

    def load_cached_memberships(self) -> dict[str, list]:
        """Load cached memberships from CSV file"""
        memberships: dict[str, list] = {}

        if not LIST_MEMBERSHIPS_FILE.exists():
            return memberships

        try:
            with open(LIST_MEMBERSHIPS_FILE, "r", encoding="utf-8") as f:
                logger.info("Loading cached memberships from %s", LIST_MEMBERSHIPS_FILE)
                reader = csv.DictReader(f)
                for row in reader:
                    list_id = row["list_id"]
                    if list_id not in memberships:
                        memberships[list_id] = []
                    memberships[list_id].append(
                        {"user_id": row["user_id"], "list_name": row["list_name"]}
                    )
        except (csv.Error, IOError, KeyError) as e:
            logger.warning("Could not load cached memberships: %s", e)

        return memberships

    def save_memberships(self, all_memberships: dict[str, list]):
        """Save all memberships to CSV file"""
        LIST_MEMBERSHIPS_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(LIST_MEMBERSHIPS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["user_id", "list_id", "list_name"])

            for list_id, members in all_memberships.items():
                for member in members:
                    writer.writerow([member["user_id"], list_id, member["list_name"]])

    def update_cache(self):
        """Main update logic using member count optimization"""
        logger.info("Starting list membership cache update...")

        # Load existing cache
        cached_metadata = self.load_cached_metadata()
        cached_memberships = self.load_cached_memberships()

        # Get current user and lists
        lists_response = self.twitter_client.get_owned_lists()
        current_lists = lists_response.get("data", [])

        # Track changes
        updated_lists = []
        current_memberships = {}

        for i, list_info in enumerate(current_lists):
            list_id = list_info["id"]
            list_name = list_info["name"]
            member_count = list_info.get("member_count", 0)

            # Check if we need to fetch members
            cached_info = cached_metadata.get(list_id, {})
            cached_count = cached_info.get("member_count", -1)

            if member_count != cached_count:
                logger.info(
                    "Member count changed for '%s' (%s -> %s), fetching members...",
                    list_name, cached_count, member_count
                )
                members_response = self.twitter_client.get_list_members(list_id)
                members = members_response.get("data", [])
                current_memberships[list_id] = [
                    {"user_id": member["id"], "list_name": list_name}
                    for member in members
                ]
                updated_lists.append(list_name)

                # Rate limit protection between list fetches
                if i < len(current_lists) - 1:  # Only sleep if not the last list
                    logger.info("Waiting 15 minutes before next list...")
                    sleep_with_jitter(15 * 60)
            else:
                logger.info(
                    "No change in member count for '%s' (%s), using cached data...",
                    list_name, member_count
                )
                # Use cached memberships if available
                current_memberships[list_id] = cached_memberships.get(list_id, [])

            # Update metadata
            cached_metadata[list_id] = {
                "name": list_name,
                "member_count": member_count,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        # Save updated cache files
        self.save_metadata(cached_metadata)
        self.save_memberships(current_memberships)

        logger.info(
            "Cache update complete. Updated %d lists: %s",
            len(updated_lists), ', '.join(updated_lists) if updated_lists else 'none'
        )


def main() -> int:
    """Main entry point"""
    try:
        twitter_client = create_twitter_client()
        updater = ListMembershipUpdater(twitter_client)
        updater.update_cache()
        return 0
    except ValueError as e:
        logger.error("Configuration error: %s", e, exc_info=True)
        return 1
    except TwitterAPIError as e:
        logger.error("Twitter API error: %s", e, exc_info=True)
        return 1
    except Exception as e:
        logger.error("Error updating list cache: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
