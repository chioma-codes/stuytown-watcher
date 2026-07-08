"""
StuyTown Affordable Housing Apartment Watcher
------------------------------------------------
Loads https://affordable-housing.stuytown.com/apartments/ with a headless
browser (so JavaScript-rendered content actually loads), extracts the
visible text, and compares it against the last saved version.

If the content changed, it sends a free push notification via ntfy.sh.

State is stored in last_seen.txt, which this script overwrites each run.
The GitHub Actions workflow commits that file back to the repo so state
persists between scheduled runs.
"""

import hashlib
import os
import sys
import urllib.request

from playwright.sync_api import sync_playwright

URL = "https://affordable-housing.stuytown.com/apartments/"
STATE_FILE = "last_seen.txt"

# Set this to whatever topic name you choose in the ntfy app.
# Pick something unique/hard to guess -- anyone who knows the topic
# name can see your notifications, since ntfy topics aren't private by default.
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "changeme-stuytown-alerts-93kd")


def fetch_rendered_text(url: str) -> str:
    """Load the page in a headless browser and return the visible text."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=60000)
        # Give any lazy-loaded content a moment to settle.
        page.wait_for_timeout(3000)
        text = page.inner_text("body")
        browser.close()
    return text


def notify(message: str) -> None:
    """Send a free push notification via ntfy.sh."""
    req = urllib.request.Request(
        url=f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={
            "Title": "StuyTown apartments page changed",
            "Priority": "high",
            "Tags": "house,bell",
        },
        method="POST",
    )
    urllib.request.urlopen(req, timeout=15)


def main() -> None:
    current_text = fetch_rendered_text(URL)
    current_hash = hashlib.sha256(current_text.encode("utf-8")).hexdigest()

    previous_hash = ""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            previous_hash = f.read().strip()

    if current_hash != previous_hash:
        print("Change detected.")
        if previous_hash:  # don't fire a notification on the very first run
            notify(
                f"The apartments page changed. Check it now:\n{URL}"
            )
        else:
            print("First run -- baseline saved, no notification sent.")

        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write(current_hash)
    else:
        print("No change.")

    # Always save the raw text too, for your own reference/debugging.
    with open("last_seen_full_text.txt", "w", encoding="utf-8") as f:
        f.write(current_text)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error during check: {e}", file=sys.stderr)
        sys.exit(1)
