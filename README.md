# StuyTown Apartments Page Watcher (Free)

Checks https://affordable-housing.stuytown.com/apartments/ every 10 minutes
from 7:00am-10:15am ET daily, and sends a free push notification to your
phone the moment the listed content changes. Runs entirely on GitHub's free
servers — nothing needs to stay running on your own computer.

## Setup checklist
- [x] check_apartments.py created
- [x] .github/workflows/check.yml created
- [ ] ntfy.sh topic created and NTFY_TOPIC secret added
- [ ] First manual test run completed

## Adjusting the check window/frequency
Edit the cron lines in `.github/workflows/check.yml`. GitHub Actions cron
runs on UTC time — NYC is currently UTC-4 (EDT). This will shift by an hour
when NYC switches to EST in November.

## Troubleshooting
- **No notifications ever arrive**: double check the `NTFY_TOPIC` secret
  matches exactly what you subscribed to in the ntfy app (case-sensitive).
- **Workflow fails**: go to the Actions tab, click the failed run, and read
  the error log. Most common cause is a page-load timeout.
- **Too many false-positive alerts**: the page may have some auto-changing
  element unrelated to listings. Let Claude know and the script can be
  adjusted to target a specific section instead of the whole page.
