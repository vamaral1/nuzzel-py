# User Configuration
# This file contains user preferences for the Twitter digest service

# Interest categories for tweet categorization
# The service will use these categories to organize tweets in the digest
INTERESTS = [
    "philosophy",
    "religion",
    "music",
    "artificial intelligence",
    "cultural trends",
    "relationships",
    "art",
]

# Twitter API fields to fetch https://docs.x.com/x-api/fundamentals/data-dictionary
## These fields are requested for all tweet API calls
TWEET_FIELDS = [
    "attachments",
    "author_id",
    "created_at",
    "entities",
    "public_metrics",
    "text",
    "context_annotations",
    "referenced_tweets"
]

## These expansions are requested for all tweet API calls to get referenced tweets, media, and author information
TWEET_EXPANSIONS = [
    "author_id",
    "attachments.media_keys",
    "referenced_tweets.id",
    "referenced_tweets.id.attachments.media_keys",
]

## These media fields are requested for all tweet API calls that include media
MEDIA_FIELDS = [
    "alt_text",
    "type",
    "url",
]

# Default time window for digest (in days)
# Can be overridden via DIGEST_TIME_WINDOW_DAYS environment variable
DEFAULT_TIME_WINDOW_DAYS = 1
