# Themes: per-chunk extraction

You are summarizing one **subset** of tweets from a user's timeline (chunk {chunk_index} of {chunk_count}). A later step will merge chunks into one digest.

## Tweets in this chunk (JSON)
```json
{tweets_json}
```

## Instructions
1. Identify **2–4** prominent themes in **this chunk only** (not the full day).
2. For each theme, pick **1–3 tweet IDs** from the JSON above that best represent it.
3. Write **notes**: one or two sentences describing what this chunk covers (for merging).

## Output
Return **only** a JSON object:
```json
{{
  "notes": "Short description of this chunk for merging",
  "themes": [
    {{
      "theme": "Short theme label",
      "description": "One sentence",
      "tweet_ids": ["id_from_this_chunk_only"]
    }}
  ]
}}
```

No markdown fences or extra text outside the JSON object.
