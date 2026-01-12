# Personal Daily Twitter Digest Service

## Executive Overview

You are building a **personal daily Twitter digest service** that aggregates all tweets from a user's followers, filters out noise, and delivers an intelligent summary via email. The service runs as a scheduled job on free hosting and uses LLM APIs to provide contextual insights and summarization. This is a personal tool to escape the exhausting X/Twitter feed experience where important tweets from followed accounts are often hidden.

---

## Product Definition
### Mission

Build a simple, automated service that:
1. Fetches all tweets from a user's Twitter followers published in the previous user-defined time window
2. Aggregates and deduplicates content (especially shared links/articles)
3. Uses an LLM API to generate intelligent insights, summaries, and themes from the period's tweets
4. Emails a beautifully formatted digest

### Target User

**Primary User**: Someone who follows 500+ accounts on Twitter and is frustrated by:
- Missing important tweets from people they follow
- Too much noise and low-quality content
- Time wasted scrolling through algorithmic feeds
- Wanting a single daily summary instead of constant notifications

---

## Features
#### Email Header
- **Subject Line**: "Your Twitter Digest: [Date] - [Key Theme/Highlight]"
- **Summary Stats**: Total tweets processed, number of unique accounts that tweeted, number of links shared

#### Section 1: Top Highlights (LLM-Generated)
- **AI Summary**: 2-3 paragraph overview of the most prominent themes
- **Key Insights**: What the LLM identified as noteworthy or interesting based on the user's current interests
- **On Error**: Fill in section with message "Error getting top themes" so that user can search in logs and debug

#### Section 2: Shared Links & Articles
- **Link Cleaning**:
  - Remove tracking parameters (UTM parameters, ref codes, etc.)
  - Normalize URLs (remove trailing slashes, convert to HTTPS, etc.)
  - Extract canonical URLs
- **Organization by Domain**: All canonical URLs grouped by source domain
- **For each canonical URL**, include:
  - Title
  - Number of times shared
  - Links to original tweets that shared the link
- **On Error**: Fill in section with message "Error filtering links and articles" and display the first 250 characters of the error message so the user can go back and debug

#### Section 3: Top Engagement Tweets
- **Normalization**: Engagement metrics (likes, retweets) are normalized by follower count to give all accounts equal opportunity
  - Formula: `normalized_score = engagement_count / follower_count`
  - Prevents large accounts from dominating; surfaces quality content from smaller accounts
- **Top 5 Liked Tweets (Overall)**: Highest normalized like engagement from all followers
- **Top 5 Retweeted Tweets (Overall)**: Highest normalized retweet engagement from all followers
- **Top Tweets by List**: For each Twitter list the user owns:
  - Top 5 Liked Tweets from this list (normalized by follower count)
  - Top 5 Retweeted Tweets from this list (normalized by follower count)
- **Display Format**: Tweet content, author, engagement counts (raw and normalized), link to original tweet
- **On Error**: Fill in section with message "Error finding top engaged tweets" so that user can search in logs and debug

#### Section 4: Tweets by Interest Category
- **Interest-Based Curation**: Show 5 random tweets for each of the user's configured interest categories
- **Categorization Method**: 
  - Use LLM to classify tweets into interest categories
  - Or use keyword matching as fallback/primary method
- **Random Selection**: For each category, randomly select 5 tweets from all tweets that match that category
- **Display Format**: Tweet content, author, engagement counts, link to original tweet
- **Configurable**: User can add/remove interest categories in preferences
- **On Error**: Fill in section with message "Error finding tweets for interests" so that user can search in logs and debug

#### Section 5: Top Discovered Categories
- **Category Discovery**: Aggregate tweets by context annotations and display the top 5 annotations
- **On Error**: Fill in section with message "Error aggregating annotations" so that user can search in logs and debug

#### Section 6: Most Likely to Like and Retweet
- **Personalized Recommendations**: Uses LLM to predict which tweets from the current timeline the user is most likely to engage with
- **Prediction Context**:
  - Pass the last 10 tweets the user liked as context
  - Pass the last 10 tweets the user posted (including retweets/replies) as context
  - If the user has no tweets, skip this section
  - LLM analyzes patterns in engagement behavior (topics, authors, style, etc.)
  - LLM selects the tweet from the current timeline that the user is most likely to retweet and the one they are most likely to like
  - Display the recommended tweets with explanation of why they match the user's patterns
- **Display Format**: 
  - Tweet content, author, link to original tweet
  - Brief LLM explanation of why this tweet was selected based on past behavior
- **On Error**: Fill in section with message "Error predicting which tweet you will like or retweet" so that user can search in logs and debug


