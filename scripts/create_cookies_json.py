#!/usr/bin/env python3
"""
Script to create cookies.json from cookies copied from browser dev tools.

Usage:
    python scripts/create_cookies_json.py

The script will prompt you to paste the cookies from the browser dev tools
Application tab. Paste the cookies (tab-separated format) and press Ctrl+D
(or Ctrl+Z on Windows) when done.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


def parse_cookies_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Parse cookies from tab-separated text format (from browser dev tools).

    Expected format (tab-separated):
    Name    Value    Domain    Path    Expires    Size    HttpOnly    Secure    SameSite    ...

    Args:
        text: Tab-separated cookie data from browser dev tools

    Returns:
        List of cookie dictionaries in Playwright format
    """
    cookies = []
    lines = text.strip().split('\n')

    # Skip header line if present
    if lines and ('Name' in lines[0] or 'Cookie' in lines[0]):
        lines = lines[1:]

    for line in lines:
        if not line.strip():
            continue

        parts = line.split('\t')
        if len(parts) < 4:
            # Try splitting by multiple spaces as fallback
            parts = [p for p in line.split('  ') if p.strip()]

        if len(parts) < 4:
            print(f"Warning: Skipping malformed line: {line[:50]}...")
            continue

        name = parts[0].strip()
        value = parts[1].strip()
        domain = parts[2].strip()
        path = parts[3].strip() if len(parts) > 3 else '/'

        # Parse expires date if present
        expires = None
        if len(parts) > 4 and parts[4].strip():
            expires_str = parts[4].strip()
            try:
                # Try parsing ISO format: 2026-01-10T03:31:22.101Z
                if 'T' in expires_str:
                    expires_dt = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                    expires = int(expires_dt.timestamp())
                # Try parsing as epoch timestamp
                elif expires_str.isdigit():
                    expires = int(expires_str)
            except (ValueError, AttributeError):
                pass

        # Check HttpOnly flag (usually column 6, index 5)
        http_only = False
        if len(parts) > 5:
            http_only = '✓' in parts[5] or 'true' in parts[5].lower()

        # Check Secure flag (usually column 7, index 6)
        secure = False
        if len(parts) > 6:
            secure = '✓' in parts[6] or 'true' in parts[6].lower()

        # Parse SameSite (usually column 8, index 7)
        same_site = None
        if len(parts) > 7 and parts[7].strip():
            same_site_val = parts[7].strip()
            if same_site_val.lower() in ('lax', 'strict', 'none'):
                same_site = same_site_val.capitalize()

        cookie = {
            "name": name,
            "value": value,
            "domain": domain,
            "path": path,
        }

        if expires:
            cookie["expires"] = expires

        if http_only:
            cookie["httpOnly"] = True

        if secure:
            cookie["secure"] = True

        if same_site:
            cookie["sameSite"] = same_site

        cookies.append(cookie)

    return cookies


def main():
    """Main function to create cookies.json file."""
    print("=" * 60)
    print("Twitter Cookies JSON Creator")
    print("=" * 60)
    print()
    print("Paste your cookies from the browser dev tools Application tab.")
    print("(Tab-separated format)")
    print()
    print("Press Ctrl+D (or Ctrl+Z on Windows) when done, or enter a blank line.")
    print()

    # Read cookies from stdin
    lines = []
    try:
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
    except EOFError:
        pass

    if not lines:
        print("Error: No cookies provided.")
        sys.exit(1)

    text = '\n'.join(lines)

    try:
        cookies = parse_cookies_from_text(text)

        if not cookies:
            print("Error: No valid cookies found.")
            sys.exit(1)

        # Create cookies.json in project root
        project_root = Path(__file__).parent.parent
        cookies_file = project_root / "cookies.json"

        # Write cookies to file
        with open(cookies_file, 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"\n✓ Successfully created cookies.json with {len(cookies)} cookies")
        print(f"  Location: {cookies_file}")
        print()
        print("Cookies created:")
        for cookie in cookies:
            print(f"  - {cookie['name']} ({cookie['domain']})")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
