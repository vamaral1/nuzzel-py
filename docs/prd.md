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
- **Subject Line**: "Your Twitter Digest: [Month], [Day] [Year]" (e.g. `Your Twitter Digest: March, 20 2025`)
- **Summary Stats**: Total tweets processed, number of unique accounts that tweeted, number of links shared

#### Section 1: Top Highlights (LLM-Generated)
- **Highlights**: 3–7 concise bullet points for standout themes (no long narrative intro)
- **Optional summary**: If provided by the model, show a short markdown summary under the bullets
- **On Error**: Fill in section with message "Error getting top themes" so that user can search in logs and debug

#### Section 2: Unified Tagged Tweet Feed (Curated Tweets)
- **Single feed UI**: Display one card per unique tweet across all curated sources (themes, top liked/retweeted, lists, interest categories, shared links, and personalized predictions).
- **Deduplication**: If the same tweet matches multiple sources, it is shown once and receives **multiple tags**.
- **Tagging**: Each card shows one or more tag chips indicating which sources the tweet matched (e.g. `Theme: ...`, `Top Liked` / `Top Retweeted`, the Twitter list name plus `Top Liked` or `Top Retweeted` when the tweet appears in that list’s picks, `Interest: ...`, `Shared link`, `Most Likely to Like`, etc.).
- **Feed ordering**: Tweets are sorted by the number of tags (most cross-cutting first), with engagement metrics as tie-breakers.
- **Display Format**: Tweet text + engagement metrics + View Tweet link, plus the tags label.
- **Shared links & predictions**: These are no longer rendered as standalone blocks; instead they contribute to the unified feed and tags.


