# Themes merge (consolidation)

You previously analyzed timeline tweets in **separate chunks**. Each entry below has `chunk_index`, `notes`, and `themes` from one chunk. Your job is to produce **one** coherent digest for the user.

## Per-chunk results (JSON)
```json
{chunks_json}
```

## Instructions
1. Read all chunk `notes` and `themes` and merge overlapping topics into **3–5** major themes for the full window.
2. For each final theme, keep **1–3 representative tweet IDs** (must appear in the data above).
3. Write **3–7** `highlights`: concise bullet-style strings for what stands out across the whole period—**no** multi-paragraph narrative, no filler transitions between ideas (each string is one scannable point).

## Output
Return **only** a JSON object with this structure:
```json
{{
  "highlights": [
    "Merged standout point one",
    "Merged standout point two",
    "Three to seven strings total"
  ],
  "themes": [
    {{
      "theme": "Theme name",
      "description": "Brief description",
      "tweet_ids": ["tweet_id_1", "tweet_id_2"]
    }}
  ]
}}
```

No markdown fences or extra text outside the JSON object.
