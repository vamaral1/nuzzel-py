# Technical Design Document: Personal Twitter Digest Service

## Document Purpose

This document specifies the technical architecture, requirements, and design decisions for a personal Twitter digest service. It serves as the blueprint for implementation, defining what must be built, how components interact, and the constraints that guide development decisions.

---

## 1. System Overview

### 1.1 Architecture

The service is a **stateless, scheduled job** that runs at user-configured intervals. Each execution is independent and requires no persistent database or state management between runs.

**Core Workflow:**
1. Fetch tweets from the user's Twitter timeline within a configured time window
2. Process and analyze tweets using LLM APIs
3. Generate a formatted email digest
4. Send the digest via email service

### 1.2 Key Design Principles

- **Statelessness**: Each run is independent; no database required
- **Cost-Effective**: Leverage free-tier services where possible
- **Resilience**: Graceful error handling with fallback mechanisms
- **Flexibility**: Support multiple authentication and data collection methods
- **Testability**: Mock data support for local development and testing

### 1.3 Deployment Model

- **Hosting**: GitHub Actions (free tier: 2,000 minutes/month)
- **Scheduling**: Cron-based scheduling via GitHub Actions workflows
- **Execution**: Single job per digest generation

---

## 2. Technology Stack

### 2.1 Programming Language

- **Python 3.11+**
  - Modern async/await support for concurrent operations
  - Rich ecosystem for API integrations and web automation

### 2.2 Core Dependencies

The following libraries are required:

- **Twitter Data Collection**:
  - `xdk` - Official Twitter Python SDK (for paid API access)
  - `playwright` - Headless browser automation (for non-paid access)
  - `playwright-stealth` - Anti-detection measures for browser automation

- **LLM Integration**:
  - `google-genai` - Google Gemini API client
  - `groq` - Groq API client (backup)
  - `requests` - HTTP client for OpenRouter API (backup)

- **Email Service**:
  - `mailjet-rest` - Mailjet email API client

- **Utilities**:
  - `python-dotenv` - Environment variable management
  - `jinja2` - Email template rendering
  - `markdown` - Markdown to HTML conversion for email content
  - `beautifulsoup4` - HTML parsing for URL cleaning
  - `tenacity` - Retry logic with exponential backoff

- **Testing**:
  - `pytest` - Testing framework
  - `requests-mock` - Mock HTTP responses for testing

---

## 3. Twitter Data Collection Requirements

### 3.1 Dual-Mode Support

The service **must support two distinct approaches** for collecting Twitter data, selectable via configuration:

1. **Official Twitter API (XDK)** - For users with paid Twitter API access
2. **Browser Automation (Playwright)** - For users without paid API access

The selection mechanism must be configurable via environment variable (`TWITTER_CLIENT_TYPE`).

### 3.2 Option A: Official Twitter API (XDK) - Paid Account Support

#### 3.2.1 Requirements

**Target Users**: Users with paid Twitter API subscriptions that provide sufficient rate limits for daily digest generation.

**Authentication**:
- OAuth 1.0 User Context authentication (primary)
- OAuth 2.0 support (optional)
- Required credentials:
  - `TWITTER_API_KEY`
  - `TWITTER_API_SECRET`
  - `TWITTER_ACCESS_TOKEN`
  - `TWITTER_ACCESS_TOKEN_SECRET`

**Implementation Library**: Official Twitter XDK (Python SDK)

#### 3.2.2 Data Collection Endpoints

**Primary: User Timeline**
- **Endpoint**: `GET /2/users/:id/timelines/reverse_chronological`
- **Purpose**: Fetch tweets from accounts the user follows within the configured time window
- **Rate Limits**: Varies by subscription tier
  - Free tier: 1 request / 15 minutes (insufficient for daily digests)
  - Paid tiers: Higher limits required for production use
- **Pagination**: Support up to 3 pages (300 tweets maximum)
  - `max_results`: 100 per page
  - `pagination_token`: For subsequent pages
  - Rate limit handling: 15-minute waits between pages if required
- **Query Parameters**:
  - `start_time`: ISO 8601 UTC timestamp (calculated as current time minus configured interval)
  - `expansions`: `referenced_tweets.id`, `attachments.media_keys`, `author_id`
  - `tweet.fields`: `article`, `attachments`, `author_id`, `card_uri`, `created_at`, `entities`, `public_metrics`, `text`, `context_annotations`
  - `media.fields`: `alt_text`, `type`, `url`
  - `user.fields`: `username`, `public_metrics` (followers_count)

**Secondary: Lists Management**
- **Get User's Lists**: `GET /2/users/:id/owned_lists`
  - Rate limit: 1 request / 24 hours (cacheable)
  - Fields: `id`, `name`, `member_count`
  - Pagination support: `max_results` (100 max), `pagination_token`
- **Get List Members**: `GET /2/lists/:id/members`
  - Rate limit: 1 request / 15 minutes per list
  - Only fetch when membership count changes (optimization)
  - Fields: `user_id` via expansions
  - Pagination support: `max_results` (100 max), `pagination_token`

**Tertiary: User Engagement History**
- **Liked Tweets**: `GET /2/users/:id/liked_tweets`
  - Purpose: Fetch last 10 tweets the user liked
  - Rate limit: 1 request / 15 minutes
  - Fields: Same as timeline endpoint
- **User's Tweets**: `GET /2/users/:id/tweets`
  - Purpose: Fetch last 10 posts the user made
  - Rate limit: 1 request / 15 minutes
  - Fields: Includes `referenced_tweets` for retweet detection

#### 3.2.3 Data Structure Requirements

- **Tweet Entities**: Extract link/article titles from `entities.urls[].title` field
- **Context Annotations**: Full support for Twitter's context annotation system (required for Section 5 of digest)
- **Referenced Tweets**: Support for retweets, quote tweets, and replies via `referenced_tweets` field

#### 3.2.4 Limitations

- **Free Tier Insufficient**: Free tier (100 posts/month) cannot support daily digest generation
- **Paid Tier Required**: Production use requires paid API subscription with adequate rate limits
- **Rate Limit Management**: Must implement proper rate limit handling and backoff strategies

---

### 3.3 Option B: Browser Automation (Playwright) - Non-Paid Account Support

#### 3.3.1 Requirements

**Target Users**: Users without paid Twitter API access who need an alternative data collection method.

**Authentication Methods** (must support both):
1. **Session Cookies** (recommended for CI/CD)
   - Export cookies from authenticated browser session
   - Inject cookies into Playwright browser context
   - Format: JSON array of cookie objects
2. **Full Login Automation** (fallback)
   - Automated login flow with username/password
   - Handle 2FA limitations (see Section 3.3.5)

**Implementation Library**: Playwright for headless browser automation


#### 3.3.2 Data Collection Strategy

**Primary Method: GraphQL Response Interception**
- Intercept Twitter's internal GraphQL API responses
- Extract structured data from intercepted responses (more reliable than DOM parsing)
- Target endpoints:
  - `HomeTimeline` - For timeline data
  - `UserTweets` - For user's own tweets
  - `Likes` - For user's liked tweets
  - `ListsManagementPageTimeline` - For user's lists
  - `ListMembers` - For list membership data

**Fallback Method: DOM Scraping**
- Fall back to DOM parsing if GraphQL interception fails
- Extract tweet data from rendered HTML elements
- Less reliable but provides redundancy

**Data Mapping**: Map GraphQL response format to standard tweet format matching API structure for consistency

#### 3.3.3 Data Collection Workflows

**Timeline Data Collection**:
- Navigate to `https://twitter.com/`
- Set up response interception for GraphQL endpoints
- Infinite scroll with human-like delays (2-4 seconds between scrolls)
- Collect tweets until time window boundary or maximum limit reached
- Extract: tweet text, author, timestamp, engagement metrics, user information, links, entities

**Lists Data Collection**:
- Navigate to `https://twitter.com/i/lists` to fetch list metadata
- For each list, navigate to `https://twitter.com/i/lists/{list_id}/members` to fetch members
- Intercept `ListsManagementPageTimeline` and `ListMembers` GraphQL responses
- Fallback to DOM scraping if interception fails

**User Engagement History**:
- Liked tweets: Navigate to `https://twitter.com/{user_id}/likes`, intercept `Likes` responses
- User's tweets: Navigate to `https://twitter.com/{user_id}`, intercept `UserTweets` responses
- Scroll to collect data (last 10 items required)

#### 3.3.4 Anti-Detection Requirements

To minimize detection risk, the service must implement:

- **Stealth Measures**: Use `playwright-stealth` or equivalent to mask automation signatures
- **Human-like Behavior**:
  - Random delays between actions (2-5 seconds)
  - Randomized scroll patterns
  - Realistic viewport sizes and user agents
  - Random mouse movements (optional, for headed mode)
- **Browser Configuration**:
  - Disable automation flags (`--disable-blink-features=AutomationControlled`)
  - Use realistic user agent strings
  - Standard viewport dimensions (1920x1080)

#### 3.3.5 Limitations and Constraints

**Authentication Limitations**:
- **2FA Complexity**:
  - SMS/Email 2FA: Cannot be fully automated
  - TOTP: Can be automated but requires storing secret (security risk)
  - Push notification 2FA: Not automatable
  - Not a requirement for initial release
- **Session Expiry**:
  - Cookies expire approximately every 30 days
  - Login sessions may be invalidated by Twitter
  - Requires periodic manual intervention to refresh credentials

**Data Limitations**:
- **No Context Annotations**: Twitter's web UI doesn't expose context annotations
  - Section 5 of digest (Top Discovered Categories) must be skipped or use alternative methods (e.g., LLM-based categorization)
- **Limited Media Metadata**: May have less metadata compared to official API
- **Client-Side Filtering**: No server-side `start_time` filtering; must filter in application code
- **Fragility**: UI changes can break scraping logic

#### 3.3.6 Error Handling Requirements

- Detect when scraping is blocked or fails
- Implement retry logic with exponential backoff
- Log extensively for debugging when things break
- Graceful degradation when data collection fails

---

## 4. LLM Integration Requirements

### 4.1 Multi-Provider Support

The service must support multiple LLM providers with a fallback chain to ensure reliability and cost-effectiveness.

### 4.2 Primary Provider: Google AI Studio (Gemini API)

**Requirements**:
- Free tier: 15 requests/minute, 1,500 requests/day
- Alternative limits: Up to 60 req/min, 300K tokens/day (model-dependent)
- Access: [aistudio.google.com](https://aistudio.google.com)
- API client: `google-genai` library

### 4.3 Backup Provider #1: Groq API

**Requirements**:
- Free tier: 30 requests/minute, 14,400 requests/day
- No credit card required (email or GitHub signup)
- Fast inference speeds
- Supports: Llama, Mixtral, and other models
- Access: [console.groq.com](https://console.groq.com)

### 4.4 Backup Provider #2: OpenRouter

**Requirements**:
- Free tier: Free model variants (ending in `:free`)
  - Rate limit: 20 requests/minute
  - Daily limits:
    - If purchased < 10 credits: 50 requests/day
    - If purchased >= 10 credits: 1,000 requests/day
- DDoS protection applies; negative credit balance causes 402 errors
- No credit card required for free tier (may need credits for higher limits)
- Access to multiple models from various providers
- Access: [openrouter.ai](https://openrouter.ai)

### 4.5 LLM Processing Strategy

To optimize rate limits and token usage, the service must use a **batching strategy**:

1. **Section 1 (Themes)**: Single request with all processed tweets to generate high-level summary and insights
2. **Section 4 (Interests)**: Single request with all processed tweets and user's interest categories for classification and selection
3. **Section 6 (Engagement Prediction)**: Single request containing:
   - All tweets from configured time window
   - User's last 10 liked tweets
   - User's last 10 posted tweets
   - Request: Predict top 1 most likely to like and top 1 most likely to retweet

**Error Handling**: If a batch request fails, display error message in the specific section per PRD requirements.

### 4.6 Rate Limit Handling

- **On Rate Limit Error**: Wait until next minute window (60 seconds) before retry
- **Retry Strategy**: Maximum 3 retry attempts per operation
- **Fallback Chain**: Automatically fall back to next provider if primary fails

---

## 5. Email Service Requirements

### 5.1 Provider: Mailjet

**Selection Rationale**: Free tier suitable for personal use

**Free Tier Specifications**:
- 6,000 emails/month
- 200 emails/day
- Free forever (not a trial)
- Full API access

### 5.2 Email Format Requirements

**API Endpoint**: Send API v3.1

**Content Requirements**:
- HTML email support
- Template rendering via Jinja2
- Configurable From/To email addresses
- Dynamic subject line generation

**Template Structure**: See PRD for detailed section requirements

---

## 6. Data Processing Requirements

### 6.1 URL Normalization

**Requirements**:
1. Parse URL with standard library (`urllib.parse`)
2. For entities, use `expanded_url` instead of `url` (which may be wrapped in `t.co` shortener)
3. Remove tracking parameters (`utm_*`, `ref`, `source`, etc.)
4. Normalize scheme (default to HTTPS)
5. Remove trailing slashes
6. Extract canonical URL when possible

### 6.2 Engagement Normalization

**Formula**: `normalized_score = engagement_count / follower_count`

**Purpose**: Prevent large accounts from dominating; surface quality content from smaller accounts

**Application**: Used in Section 3 (Top Engagement Tweets) for ranking

### 6.3 Context Annotations Processing

**Data Structure**: Context annotations are nested objects with domain and entity information:

```json
"context_annotations": [
  {
    "domain": {
      "id": "29",
      "name": "Events [Entity Service]",
      "description": "Real world events."
    },
    "entity": {
      "id": "1186637514896920576",
      "name": "New Years Eve"
    }
  }
]
```

**Processing Requirements** (for Section 5):
1. Extract `context_annotations` from all tweets in time window
2. Group entities by domain name
3. Count total occurrences per domain
4. Sort domains by total frequency (descending)
5. Display top 5 domains with all associated entity names and individual counts

**Note**: Context annotations are only available via official Twitter API. When using browser automation, Section 5 must be skipped or use alternative categorization methods (e.g., LLM-based).

---

## 7. List Management Requirements

### 7.1 Caching Strategy

To optimize API usage and avoid Twitter API rate limits, list membership data must be cached if not in headless browser mode.

**List Metadata Cache**:
- **File**: `data/list_metadata.json`
- **Format**: JSON object mapping list IDs to metadata
- **Fields**: `name`, `member_count`, `last_updated`
- **Purpose**: Track list member counts to detect changes

**List Membership Cache**:
- **File**: `data/list_memberships.csv`
- **Format**: CSV with headers `user_id,list_id,list_name`
- **Purpose**: Cache list membership to avoid API calls during daily digest
- **Optional**: If file is missing or empty, daily digest must skip list-specific sections gracefully

### 7.2 Update Workflow

**Separate Job**: List membership updates must run in a separate scheduled job (monthly or on-demand)

**Update Logic**:
1. Check `data/list_metadata.json` (create if missing)
2. Fetch all user's lists (including `member_count`)
3. For each list:
   - Compare current `member_count` with cached value
   - If `member_count` changed (or list is new): fetch members and update cache
   - If `member_count` unchanged: skip member fetching
4. Update `data/list_metadata.json` with current member counts and timestamps
5. Update `data/list_memberships.csv` only for lists that changed

**Daily Digest Job**: Reads from cached CSV file (no API calls needed)

---

## 8. Error Handling and Resilience

### 8.1 Retry Strategy

**Library**: Tenacity (or equivalent retry library)

**Retry Requirements**:
- **Browser Client**: Human-like delays (2-5 seconds random) between actions
- **LLM APIs**: Wait until next minute window (60 seconds) on rate limit errors
- **Network Errors**: Exponential backoff with jitter
- **Maximum Retries**: 3 attempts per operation
- **Browser-Specific**: Random mouse movements and scroll patterns (when in headed mode)

### 8.2 Logging Requirements

**Logging Levels**: Use Python `logging` module with appropriate levels

**Required Logging**:
- All API calls (without sensitive data like tokens/passwords)
- Errors with full context
- Processing statistics (tweets processed, categories found, etc.)
- Warnings for:
  - Rate limit pagination (when fewer than 300 tweets are fetched)
  - Empty responses
  - Missing data files

**Email Integration**: Include warnings in email digest when applicable

### 8.3 Error Display in Digest

Per PRD requirements, each section must handle errors gracefully:
- Display user-friendly error messages in the affected section
- Include enough detail for debugging (e.g., first 250 characters of error message)
- Allow users to search logs for full error details

---

## 9. Configuration and Secrets Management

### 9.1 Environment Variables

**Twitter Client Selection**:
- `TWITTER_CLIENT_TYPE`: `"xdk"` or `"browser"` (default: `"browser"`)

**Twitter API (XDK) Credentials**:
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`

**Twitter Browser Client**:
- `TWITTER_SESSION_COOKIES`: JSON array of cookies (for cookie auth, preferred)
- `TWITTER_USERNAME`: Twitter username/email (for login auth, fallback)
- `TWITTER_PASSWORD`: Twitter password (for login auth, fallback)
- `BROWSER_HEADLESS`: `"true"` or `"false"` (default: `"true"`) for local debugging

**Mailjet**:
- `MAILJET_API_KEY`
- `MAILJET_API_SECRET`

**LLM APIs**:
- `GEMINI_API_KEY`
- `GROQ_API_KEY`
- `OPEN_ROUTER_API_KEY`

**Email Configuration**:
- `RECIPIENT_EMAIL`: Destination email address
- `SENDER_EMAIL`: Sender email address

**Testing**:
- `USE_MOCK`: `"true"` or `"false"` (default: `"false"`)

**Access Pattern**: Use `python-dotenv` to load `.env` file locally; GitHub Actions uses repository secrets (automatically available as environment variables).

### 9.2 Configuration Files

**User Preferences** (`constants.py` or equivalent):
- Interest categories for tweet categorization
- Configurable digest interval (in hours, e.g., 24, 48, 72)
- Default time window for digest (in days)

---

## 10. Deployment Requirements

**Workflow 1: Update List Membership**

**Purpose**: Fetch and cache list membership data

**Trigger**:
- Scheduled: First day of each month at 2:00 AM UTC
- Manual: `workflow_dispatch` for on-demand updates

**Steps**:
1. Checkout code
2. Set up Python environment
3. Install dependencies
4. Run list update script
5. Commit and push updated cache files (if changed)

**Workflow 2: Digest Generation**

**Purpose**: Generate and send Twitter digest

**Trigger**:
- Scheduled: At configured interval (e.g., every 24, 48, or 72 hours) at 5:00 AM Los Angeles time (1:00 PM UTC)
- Manual: `workflow_dispatch` for on-demand execution

**Steps**:
1. Checkout code
2. Set up Python environment
3. Install dependencies
4. Install Playwright browsers (if using browser client)
5. Run digest generation script
6. Job logs available in GitHub Actions UI

**Secrets Management**: All sensitive credentials stored as GitHub repository secrets

## 11. Local Development & Testing

**Requirements**:
1. Support running with live clients or with mock data by configuring `USE_MOCKS=true` in `.env` file
2. Support running browser client without headless browser by setting `BROWSER_HEADLESS=false` in `.env` file


**Mock Data Files Required**:
- `timeline_page1.json` - First page with `next_token`
- `timeline_page2.json` - Second page with `next_token`
- `timeline_page3.json` - Final page (no `next_token`)
- `timeline_single_page.json` - Single page response (< 100 tweets)
- `lists.json` - User's owned lists
- `list_members_*.json` - Members for each list
- `liked_tweets.json` - User's liked tweets (last 10)
- `user_posts.json` - User's posts (last 10 for retweet detection)
- `user_me.json` - Authenticated user details (for user ID fetching)


**Unit Tests Required**:
- URL normalization functions
- Engagement calculation (normalized scores)
- Link extraction
- Template rendering
- Browser client authentication methods (cookie and login)
- Browser client data extraction from GraphQL responses
- Tweet deduplication logic
- Context annotations processing

**Integration Tests Required**:
- Full pipeline with mock data
- LLM API fallback chain
- Email generation and sending (test mode)
- Single page response handling
- Multi-page pagination
- Empty response handling
- Missing list membership cache handling
- Retweet deduplication
- Network error handling

**Browser Client Specific Tests**:
- Cookie authentication
- Login authentication
- Response interception
- GraphQL data extraction
- DOM scraping fallback

---

## 12. Email Template Requirements

### 12.1 Format

- **Template Engine**: Jinja2
- **Output Format**: HTML email
- **Styling**: Inline CSS (for email client compatibility)
- **Design**: Responsive, mobile-friendly layout

### 12.2 Sections

See [PRD](./prd.md) for detailed section requirements. The template must support all sections defined in the PRD with proper error handling per section.

---

## 13. Project Structure

The following directory structure is recommended for organization:

```
nuzzel/
├── .github/
│   └── workflows/
│       ├── daily_digest.yml          # Digest generation workflow
│       └── update_lists.yml          # List membership update workflow
├── nuzzel/
│   ├── __init__.py
│   ├── main.py                       # Entry point
│   ├── constants.py                  # User configuration
│   ├── twitter_client.py             # Twitter client abstraction
│   ├── browser_twitter_client.py     # Browser-based client
│   ├── browser_utils/                 # Browser automation utilities
│   │   ├── __init__.py
│   │   ├── auth.py                   # Authentication helpers
│   │   ├── extractors.py             # Data extraction
│   │   └── stealth.py                # Anti-detection measures
│   ├── llm_client.py                 # LLM abstraction
│   ├── email_client.py               # Email service wrapper
│   ├── processors/                   # Data processing modules
│   │   ├── __init__.py
│   │   ├── tweet_processor.py        # Main processing logic
│   │   ├── link_extractor.py         # URL extraction/normalization
│   │   ├── engagement_calculator.py  # Normalized engagement scores
│   │   ├── categorizer.py            # LLM categorization
│   │   └── engagement_predictor.py   # LLM-based predictions
│   ├── generators/                   # Content generation
│   │   ├── __init__.py
│   │   ├── digest_generator.py       # Email content generation
│   │   └── template_renderer.py      # Template rendering
│   └── utils/
│       ├── __init__.py
│       └── url_utils.py              # URL normalization
├── tests/
│   ├── fixtures/
│   │   └── twitter_api/              # Mock API responses
│   └── test_*.py                     # Unit and integration tests
├── templates/
│   └── email.html                    # Jinja2 email template
├── data/
│   ├── list_metadata.json           # List metadata cache
│   └── list_memberships.csv         # List membership cache
├── requirements.txt
├── .env                             # Environment variable
├── .gitignore
├── docs/
│   ├── prd.md                        # Product requirements
│   └── tech_design.md                 # This document
└── README.md
```

---

## 14. Security Considerations

### 14.1 Credential Management

- **Never commit credentials** to version control
- Use `.gitignore` to exclude `.env` files
- Store all secrets as GitHub repository secrets for CI/CD

### 14.2 Authentication Security

- **Browser Client**: Prefer cookie-based authentication over username/password when possible

### 14.3 Data Privacy

- Log all API calls without sensitive data (tokens, passwords)
- Sanitize error messages before logging
- Ensure email content doesn't expose sensitive information

---

## 15. Performance Considerations

### 15.1 Rate Limit Optimization

- Batch LLM requests to minimize API calls
- Cache list membership data to avoid repeated API calls
- Implement intelligent pagination (stop when time window boundary reached)

### 15.2 Resource Usage

- **Browser Client**: More resource-intensive; optimize browser lifecycle (close when done)
- **Memory Management**: Process tweets in batches if memory becomes an issue
- **Timeout Handling**: Set appropriate timeouts for all network operations

### 15.3 Execution Time

- Target: Complete digest generation within 2 hours for typical use cases
- Maximum: 6-hour timeout for edge cases
- Monitor execution times and optimize slow operations

---

## References

- [Twitter API v2 Documentation](https://docs.x.com/x-api)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Mailjet API Documentation](https://dev.mailjet.com/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Product Requirements Document](./prd.md)
