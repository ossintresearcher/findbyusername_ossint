# findbyusername_ossint

# 🔎 findbyusername_ossint

**Async OSINT tool** to quickly check whether a username exists across common platforms.  
Useful for footprinting, digital profiling, and collecting public presence signals. Outputs results as JSON and CSV for analysis.

for more information : https://www.linkedin.com/in/ossintresearcher/

---

## Features
- Asynchronous, fast checks using `aiohttp`.
- Configurable platform list (URL patterns).
- Respectful rate-limiting and retries.
- Output to JSON and CSV.
- Simple CLI: specify username(s) and options.
- Easy to extend with additional platforms.

---

## WARNING / Disclaimer
This tool is intended **only for lawful, ethical OSINT and research** using publicly available information. Do **not** use it to invade privacy, harass, or perform unauthorized scraping. Always follow each platform’s Terms of Service and applicable laws in your jurisdiction.

---

## Installation

1. Clone the repo:
```bash
git clone https://github.com/<your-username>/findbyusername_ossint.git
cd findbyusername_ossint

Basic single username check:

python find_by_username.py --username alice42

Check multiple usernames from a file and output JSON:

python find_by_username.py --input usernames.txt --output results.json --format json


Help:

python find_by_username.py -h

Platforms

The tool uses configurable URL patterns to check profiles. Default platforms include:

GitHub, GitLab, Bitbucket

Twitter/X, Mastodon (example instance), Instagram

Reddit, StackOverflow

TikTok, Medium

Keybase, HackerNews

YouTube (channel/profile fallback)

Website root check (example.com/@username)

You can add or remove platforms by editing the PLATFORMS dictionary in find_by_username.py.

How it works (brief)

For each platform, the script formats the profile URL using the provided username.

It performs an HTTP GET (or HEAD where appropriate) with a polite User-Agent.

Interprets status codes and response content to determine existence:

200 usually -> exists (further heuristics applied for redirects/404 pages).

404 -> not found.

403/429 -> blocked/rate limited (reported).

Saves results with timestamp, platform, url, http_status, exists, note.
