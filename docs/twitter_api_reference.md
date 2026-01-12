# Twitter API v2 Reference

Complete reference for Twitter API v2 endpoints, rate limits, and special attributes across Pro, Basic, and Free tiers. Taken from https://developer.x.com/en/portal/products which is blocked behind authentication so AI agents don't have access to it.

---

## Tweets

### DELETE /2/tweets/:id
Delete a tweet by ID.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 17 requests / 24 hours (PER USER), 17 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### DELETE /2/users/:id/likes/:tweet_id
Remove a like from a tweet.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 100 requests / 24 hours (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### DELETE /2/users/:id/retweets/:tweet_id
Remove a retweet.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### GET /2/tweets
Retrieve multiple tweets by IDs.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER), 450 requests / 15 minutes (PER APP)
- **Basic**: 15 requests / 15 minutes (PER USER), 15 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/tweets/:id
Retrieve a single tweet by ID.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER), 450 requests / 15 minutes (PER APP)
- **Basic**: 15 requests / 15 minutes (PER USER), 15 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/tweets/:id/liking_users
Get users who liked a specific tweet.

**Rate Limits:**
- **Pro**: 75 requests / 15 minutes (PER USER), 75 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/tweets/:id/quote_tweets
Get quote tweets for a specific tweet.

**Rate Limits:**
- **Pro**: 75 requests / 15 minutes (PER USER), 75 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 5 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/tweets/:id/retweeted_by
Get users who retweeted a specific tweet.

**Rate Limits:**
- **Pro**: 75 requests / 15 minutes (PER USER), 75 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 5 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/tweets/:id/retweets
Get retweets of a tweet.

**Rate Limits:**
- **Pro**: 75 requests / 15 minutes (PER USER), 75 requests / 15 minutes (PER APP)
- **Basic**: 10 requests / 15 minutes (PER USER), 10 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/tweets/counts/all
Get total count of tweets matching a query (full archive search).

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:**
- Enhanced operators
- 1024 query length

---

### GET /2/tweets/counts/recent
Get count of tweets matching a query (recent search).

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER APP)

**Special Attributes:**
- 512 query length
- Core operators

---

### GET /2/tweets/search/all
Full archive search for tweets.

**Rate Limits:**
- **Pro**: 1 request / second (PER USER), 1 request / second (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:**
- 500 results per response
- 10 default results per response
- Enhanced operators
- 1024 query length

---

### GET /2/tweets/search/recent
Recent search for tweets.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER), 450 requests / 15 minutes (PER APP)
- **Basic**: 60 requests / 15 minutes (PER USER), 60 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:**
- 10 default results per response
- 100 results per response
- 512 query length
- Core operators

---

### GET /2/tweets/search/stream
Stream tweets matching rules (filtered stream).

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:**
- 1000 rules
- Does not support backfill
- 1024 rule length
- Enterprise
- 1 connection
- 250 Tweets per second

---

### GET /2/tweets/search/stream/rules
Get rules for filtered stream.

**Rate Limits:**
- **Pro**: 450 requests / 15 minutes (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:**
- 1000 rules
- Does not support backfill
- 1024 rule length
- Enterprise
- 1 connection
- 250 Tweets per second

---

### GET /2/tweets/search/stream/rules/counts
Get counts of stream rules.

**Rate Limits:**
- **Pro**: 1000 requests / 15 minutes (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:**
- Does not support backfill
- 50 Tweets per second
- 5 rules
- 1024 rule length
- 1 connection
- Essential

---

### GET /2/users/:id/liked_tweets
Get tweets liked by a user.

**Rate Limits:**
- **Pro**: 75 requests / 15 minutes (PER USER), 75 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 5 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/users/:id/mentions
Get tweets mentioning a user.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER), 450 requests / 15 minutes (PER APP)
- **Basic**: 10 requests / 15 minutes (PER USER), 15 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/users/:id/timelines/reverse_chronological
Get reverse chronological timeline for a user.

**Rate Limits:**
- **Pro**: 180 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### GET /2/users/:id/tweets
Get tweets posted by a user.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER), 1500 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 10 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/users/reposts_of_me
Get reposts (retweets) of the authenticated user's tweets.

**Rate Limits:**
- **Pro**: 75 requests / 15 minutes (PER USER), 75 requests / 15 minutes (PER USER)
- **Basic**: 75 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:**
- 100 results per response

---

### POST /2/tweets
Create a new tweet.

**Rate Limits:**
- **Pro**: 100 requests / 15 minutes (PER USER), 10000 requests / 24 hours (PER APP)
- **Basic**: 100 requests / 24 hours (PER USER), 1667 requests / 24 hours (PER APP)
- **Free**: 17 requests / 24 hours (PER USER), 17 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/tweets/search/stream/rules
Create or modify rules for filtered stream.

**Rate Limits:**
- **Pro**: 100 requests / 15 minutes (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:**
- 1000 rules
- Does not support backfill
- 1024 rule length
- Enterprise
- 1 connection
- 250 Tweets per second

---

### POST /2/users/:id/likes
Like a tweet.

**Rate Limits:**
- **Pro**: 1000 requests / 24 hours (PER USER)
- **Basic**: 200 requests / 24 hours (PER USER)
- **Free**: Not available

**Special Attributes:** None

---

### POST /2/users/:id/retweets
Retweet a tweet.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### PUT /2/tweets/:tweet_id/hidden
Hide or unhide a reply to a tweet.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

## Users

### DELETE /2/users/:source_user_id/following/:target_user_id
Unfollow a user.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### DELETE /2/users/:source_user_id/muting/:target_user_id
Unmute a user.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### GET /2/users
Get multiple users by IDs.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER), 300 requests / 15 minutes (PER APP)
- **Basic**: 100 requests / 24 hours (PER USER), 500 requests / 24 hours (PER APP)
- **Free**: 1 request / 24 hours (PER USER), 1 request / 24 hours (PER APP)

**Special Attributes:** None

---

### GET /2/users/:id
Get a single user by ID.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER), 300 requests / 15 minutes (PER APP)
- **Basic**: 100 requests / 24 hours (PER USER), 500 requests / 24 hours (PER APP)
- **Free**: 1 request / 24 hours (PER USER), 1 request / 24 hours (PER APP)

**Special Attributes:** None

---

### GET /2/users/:id/blocking
Get users blocked by a user.

**Rate Limits:**
- **Pro**: 15 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### GET /2/users/:id/following/spaces
Get spaces followed by a user.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER), 300 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/users/:id/muting
Get users muted by a user.

**Rate Limits:**
- **Pro**: 15 requests / 15 minutes (PER USER)
- **Basic**: 100 requests / 24 hours (PER USER)
- **Free**: 1 request / 24 hours (PER USER)

**Special Attributes:** None

---

### GET /2/users/by
Get users by usernames.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER), 300 requests / 15 minutes (PER APP)
- **Basic**: 100 requests / 24 hours (PER USER), 500 requests / 24 hours (PER APP)
- **Free**: 1 request / 24 hours (PER USER), 1 request / 24 hours (PER APP)

**Special Attributes:** None

---

### GET /2/users/by/username/:username
Get a user by username.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER), 300 requests / 15 minutes (PER APP)
- **Basic**: 100 requests / 24 hours (PER USER), 500 requests / 24 hours (PER APP)
- **Free**: 3 requests / 15 minutes (PER USER), 3 requests / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/users/by/username/:username/mentions
Get mentions for a user by username.

**Rate Limits:**
- **Pro**: 180 requests / 15 minutes (PER USER), 450 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/users/by/username/:username/tweets
Get tweets by a user by username.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER), 1500 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/users/me
Get the authenticated user.

**Rate Limits:**
- **Pro**: 75 requests / 15 minutes (PER USER)
- **Basic**: 250 requests / 24 hours (PER USER)
- **Free**: 25 requests / 24 hours (PER USER)

**Special Attributes:** None

---

### GET /2/users/search
Search for users.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER), 300 requests / 15 minutes (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### POST /2/users/:id/following
Follow a user.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: Not available

**Special Attributes:** None

---

### POST /2/users/:id/muting
Mute a user.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

## Spaces

### GET /2/spaces
Get multiple spaces by IDs.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER), 300 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/spaces/:id
Get a single space by ID.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER), 300 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/spaces/:id/buyers
Get buyers of a space.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER), 300 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/spaces/:id/tweets
Get tweets from a space.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER), 300 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/spaces/by/creator_ids
Get spaces by creator IDs.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER), 1 request / second (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / second (PER APP)
- **Free**: 1 request / second (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/spaces/search
Search for spaces.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER), 300 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

## Lists

### DELETE /2/lists/:id
Delete a list.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### DELETE /2/lists/:id/members/:user_id
Remove a member from a list.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### DELETE /2/users/:id/followed_lists/:list_id
Unfollow a list.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### DELETE /2/users/:id/pinned_lists/:list_id
Unpin a list.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### GET /2/lists/:id
Get a single list by ID.

**Rate Limits:**
- **Pro**: 75 requests / 15 minutes (PER USER), 75 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 5 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/lists/:id/members
Get members of a list.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER), 900 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/lists/:id/tweets
Get tweets from a list.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER), 900 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/users/:id/list_memberships
Get lists a user is a member of.

**Rate Limits:**
- **Pro**: 75 requests / 15 minutes (PER USER), 75 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/users/:id/owned_lists
Get lists owned by a user.

**Rate Limits:**
- **Pro**: 15 requests / 15 minutes (PER USER), 15 requests / 15 minutes (PER APP)
- **Basic**: 100 requests / 24 hours (PER USER), 500 requests / 24 hours (PER APP)
- **Free**: 1 request / 24 hours (PER USER), 1 request / 24 hours (PER APP)

**Special Attributes:** None

---

### GET /2/users/:id/pinned_lists
Get lists pinned by a user.

**Rate Limits:**
- **Pro**: 15 requests / 15 minutes (PER USER), 15 requests / 15 minutes (PER APP)
- **Basic**: 100 requests / 24 hours (PER USER), 500 requests / 24 hours (PER APP)
- **Free**: 1 request / 24 hours (PER USER), 1 request / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/lists
Create a new list.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER)
- **Basic**: 100 requests / 24 hours (PER USER)
- **Free**: 1 request / 24 hours (PER USER)

**Special Attributes:** None

---

### POST /2/lists/:id/members
Add a member to a list.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### POST /2/users/:id/followed_lists
Follow a list.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### POST /2/users/:id/pinned_lists
Pin a list.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

### PUT /2/lists/:id
Update a list.

**Rate Limits:**
- **Pro**: 300 requests / 15 minutes (PER USER)
- **Basic**: 5 requests / 15 minutes (PER USER)
- **Free**: 1 request / 15 minutes (PER USER)

**Special Attributes:** None

---

## Compliance

### GET /2/compliance/jobs
Get compliance jobs.

**Rate Limits:**
- **Pro**: 150 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/compliance/jobs/:job_id
Get a specific compliance job.

**Rate Limits:**
- **Pro**: 150 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### POST /2/compliance/jobs
Create a compliance job.

**Rate Limits:**
- **Pro**: 150 requests / 15 minutes (PER APP)
- **Basic**: 15 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

## Usage

### GET /2/usage/tweets
Get tweet usage statistics.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER APP)
- **Basic**: 50 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

## Trends

### GET /2/trends/by/woeid/:id
Get trends by Where On Earth ID (WOEID).

**Rate Limits:**
- **Pro**: 75 requests / 15 minutes (PER APP)
- **Basic**: 15 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:** None

---

### GET /2/users/personalized_trends
Get personalized trends for a user.

**Rate Limits:**
- **Pro**: 10 requests / 15 minutes (PER USER), 200 requests / 15 minutes (PER APP)
- **Basic**: 1 request / 15 minutes (PER USER), 20 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 24 hours (PER APP)

**Special Attributes:** None

---


## Uncategorized

### DELETE /2/account_activity/webhooks/:webhook_id/subscriptions/:user_id/all
Delete account activity webhook subscription for a user.

**Rate Limits:**
- **Pro**: 450 requests / 15 minutes (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### DELETE /2/activity/subscriptions/:subscription_id
Delete an activity subscription.

**Rate Limits:**
- **Pro**: 500 requests / 15 minutes (PER APP)
- **Basic**: 500 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:** None

---

### DELETE /2/connections/all
Delete all connections.

**Rate Limits:**
- **Pro**: 25 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### DELETE /2/media/subtitles
Delete media subtitles.

**Rate Limits:**
- **Pro**: 100 requests / 15 minutes (PER USER), 10000 requests / 24 hours (PER APP)
- **Basic**: 100 requests / 24 hours (PER USER), 1667 requests / 24 hours (PER APP)
- **Free**: 17 requests / 24 hours (PER USER), 17 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### DELETE /2/notes/:id
Delete a note.

**Rate Limits:**
- **Pro**: 90 requests / 15 minutes (PER USER)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### DELETE /2/webhooks/:webhook_id
Delete a webhook.

**Rate Limits:**
- **Pro**: 450 requests / 15 minutes (PER APP)
- **Basic**: 450 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:** None

---

### GET /2/account_activity/subscriptions/count
Get count of account activity subscriptions.

**Rate Limits:**
- **Pro**: 450 requests / 15 minutes (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### GET /2/account_activity/webhooks/:webhook_id/subscriptions/all
Get all account activity webhook subscriptions.

**Rate Limits:**
- **Pro**: 450 requests / 15 minutes (PER USER)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### GET /2/account_activity/webhooks/:webhook_id/subscriptions/all/list
Get list of account activity webhook subscriptions.

**Rate Limits:**
- **Pro**: 450 requests / 15 minutes (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### GET /2/activity/stream
Get activity stream.

**Rate Limits:**
- **Pro**: 450 requests / 15 minutes (PER APP)
- **Basic**: 450 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:**
- Does not support backfill
- 2 connections
- 250 Tweets per second

---

### GET /2/activity/subscriptions
Get activity subscriptions.

**Rate Limits:**
- **Pro**: 500 requests / 15 minutes (PER APP)
- **Basic**: 500 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:** None

---

### GET /2/media/upload
Get media upload status.

**Rate Limits:**
- **Pro**: 1000 requests / 15 minutes (PER USER), 100000 requests / 24 hours (PER APP)
- **Basic**: 1000 requests / 24 hours (PER USER), 16670 requests / 24 hours (PER APP)
- **Free**: 170 requests / 24 hours (PER USER), 170 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### GET /2/news/:id
Get news article by ID.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER), 50 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 5 requests / 15 minutes (PER APP)
- **Free**: 1 request / 15 minutes (PER USER), 1 request / 15 minutes (PER APP)

**Special Attributes:** None

---

### GET /2/news/search
Search for news articles.

**Rate Limits:**
- **Pro**: 50 requests / 15 minutes (PER USER), 50 requests / 15 minutes (PER APP)
- **Basic**: 5 requests / 15 minutes (PER USER), 5 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:** None

---

### GET /2/notes/search/notes_written
Search for notes written by a user.

**Rate Limits:**
- **Pro**: 180 requests / 15 minutes (PER USER)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### GET /2/notes/search/posts_eligible_for_notes
Search for posts eligible for notes.

**Rate Limits:**
- **Pro**: 90 requests / 15 minutes (PER USER)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### GET /2/webhooks
Get webhooks.

**Rate Limits:**
- **Pro**: 450 requests / 15 minutes (PER APP)
- **Basic**: 450 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:** None

---

### POST /2/account_activity/replay/webhooks/:webhook_id/subscriptions/all
Replay account activity webhook subscriptions.

**Rate Limits:**
- **Pro**: 450 requests / 15 minutes (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### POST /2/account_activity/webhooks/:webhook_id/subscriptions/all
Create account activity webhook subscription.

**Rate Limits:**
- **Pro**: 250 requests / 15 minutes (PER USER), 5000 requests / 24 hours (PER APP)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### POST /2/activity/subscriptions
Create an activity subscription.

**Rate Limits:**
- **Pro**: 500 requests / 15 minutes (PER APP)
- **Basic**: 500 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:** None

---

### POST /2/evaluate_note
Evaluate a note.

**Rate Limits:**
- **Pro**: 900 requests / 15 minutes (PER USER)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### POST /2/media/metadata
Update media metadata.

**Rate Limits:**
- **Pro**: 500 requests / 15 minutes (PER USER), 50000 requests / 24 hours (PER APP)
- **Basic**: 500 requests / 24 hours (PER USER), 8335 requests / 24 hours (PER APP)
- **Free**: 85 requests / 24 hours (PER USER), 85 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/media/metadata/create
Create media metadata.

**Rate Limits:**
- **Pro**: 500 requests / 15 minutes (PER USER), 50000 requests / 24 hours (PER APP)
- **Basic**: 500 requests / 24 hours (PER USER), 8335 requests / 24 hours (PER APP)
- **Free**: 85 requests / 24 hours (PER USER), 85 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/media/subtitles
Update media subtitles.

**Rate Limits:**
- **Pro**: 100 requests / 15 minutes (PER USER), 10000 requests / 24 hours (PER APP)
- **Basic**: 100 requests / 24 hours (PER USER), 1667 requests / 24 hours (PER APP)
- **Free**: 17 requests / 24 hours (PER USER), 17 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/media/subtitles/create
Create media subtitles.

**Rate Limits:**
- **Pro**: 500 requests / 15 minutes (PER USER), 50000 requests / 24 hours (PER APP)
- **Basic**: 500 requests / 24 hours (PER USER), 8335 requests / 24 hours (PER APP)
- **Free**: 85 requests / 24 hours (PER USER), 85 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/media/subtitles/delete
Delete media subtitles.

**Rate Limits:**
- **Pro**: 500 requests / 15 minutes (PER USER), 50000 requests / 24 hours (PER APP)
- **Basic**: 500 requests / 24 hours (PER USER), 8335 requests / 24 hours (PER APP)
- **Free**: 85 requests / 24 hours (PER USER), 85 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/media/upload
Upload media.

**Rate Limits:**
- **Pro**: 500 requests / 15 minutes (PER USER), 50000 requests / 24 hours (PER APP)
- **Basic**: 500 requests / 24 hours (PER USER), 8335 requests / 24 hours (PER APP)
- **Free**: 85 requests / 24 hours (PER USER), 85 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/media/upload/:id/append
Append to media upload.

**Rate Limits:**
- **Pro**: 1875 requests / 15 minutes (PER USER), 180000 requests / 24 hours (PER APP)
- **Basic**: 180000 requests / 24 hours (PER USER), 180000 requests / 24 hours (PER APP)
- **Free**: 180000 requests / 24 hours (PER USER), 180000 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/media/upload/:id/finalize
Finalize media upload.

**Rate Limits:**
- **Pro**: 1875 requests / 15 minutes (PER USER), 180000 requests / 24 hours (PER APP)
- **Basic**: 180000 requests / 24 hours (PER USER), 180000 requests / 24 hours (PER APP)
- **Free**: 180000 requests / 24 hours (PER USER), 180000 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/media/upload/initialize
Initialize media upload.

**Rate Limits:**
- **Pro**: 1875 requests / 15 minutes (PER USER), 180000 requests / 24 hours (PER APP)
- **Basic**: 180000 requests / 24 hours (PER USER), 180000 requests / 24 hours (PER APP)
- **Free**: 180000 requests / 24 hours (PER USER), 180000 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/notes
Create a note.

**Rate Limits:**
- **Pro**: 90 requests / 15 minutes (PER USER)
- **Basic**: Not available
- **Free**: Not available

**Special Attributes:** None

---

### POST /2/users/:id/dm/block
Block a user from sending DMs.

**Rate Limits:**
- **Pro**: 10 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Basic**: 10 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 4 requests / 15 minutes (PER USER), 10 requests / 24 hours (PER APP)

**Special Attributes:** None

---

### POST /2/users/:id/dm/unblock
Unblock a user from sending DMs.

**Rate Limits:**
- **Pro**: 10 requests / 15 minutes (PER USER), 1000 requests / 24 hours (PER APP)
- **Basic**: 10 requests / 15 minutes (PER USER), 25 requests / 15 minutes (PER APP)
- **Free**: 10 requests / 24 hours (PER USER), 10 requests / 15 minutes (PER APP)

**Special Attributes:** None

---

### POST /2/webhooks
Create a webhook.

**Rate Limits:**
- **Pro**: 450 requests / 15 minutes (PER APP)
- **Basic**: 450 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:** None

---

### POST /2/webhooks/replay
Replay webhooks.

**Rate Limits:**
- **Pro**: 100 requests / 15 minutes (PER APP)
- **Basic**: 100 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:** None

---

### PUT /2/activity/subscriptions/:subscription_id
Update an activity subscription.

**Rate Limits:**
- **Pro**: 500 requests / 15 minutes (PER APP)
- **Basic**: 500 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:** None

---

### PUT /2/webhooks/:webhook_id
Update a webhook.

**Rate Limits:**
- **Pro**: 450 requests / 15 minutes (PER APP)
- **Basic**: 450 requests / 15 minutes (PER APP)
- **Free**: Not available

**Special Attributes:** None

---

## Notes

### Rate Limit Types
- **PER USER**: Rate limit applies per authenticated user
- **PER APP**: Rate limit applies per application (shared across all users)

### Special Attributes
- **Enhanced operators**: Advanced search operators available
- **Core operators**: Basic search operators available
- **Query length**: Maximum length of search query in characters
- **Rule length**: Maximum length of stream rule in characters
- **Enterprise**: Enterprise tier feature
- **Essential**: Essential tier feature
- **Results per response**: Maximum number of results returned per API call
- **Default results per response**: Default number of results if not specified
- **Connections**: Number of concurrent connections allowed
- **Tweets per second**: Maximum throughput for streaming endpoints
