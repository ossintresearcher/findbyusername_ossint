
---

## 🧩 `find_by_username.py` (save as root of repo)

```python
#!/usr/bin/env python3
"""
find_by_username.py
Asynchronous username presence checker across multiple platforms.
Author: Your Name
License: MIT
"""

import asyncio
import aiohttp
import aiofiles
import argparse
import json
import csv
from datetime import datetime
from dateutil.tz import tzlocal
from tqdm.asyncio import tqdm

# ---- Configurable platforms ----
# Each entry maps a short key to a URL format string where {username} will be placed.
# Some sites may return 200 for non-existent users; heuristics may be required.
PLATFORMS = {
    "github": "https://github.com/{username}",
    "gitlab": "https://gitlab.com/{username}",
    "bitbucket": "https://bitbucket.org/{username}",
    "twitter": "https://twitter.com/{username}",
    "x": "https://x.com/{username}",
    "instagram": "https://www.instagram.com/{username}/",
    "reddit": "https://www.reddit.com/user/{username}",
    "stack_overflow": "https://stackoverflow.com/users/{username}",
    "keybase": "https://keybase.io/{username}",
    "medium": "https://medium.com/@{username}",
    "tiktok": "https://www.tiktok.com/@{username}",
    "mastodon_example": "https://mastodon.social/@{username}",
    "youtube": "https://www.youtube.com/@{username}",
    "hackernews": "https://news.ycombinator.com/user?id={username}"
}

# ---- HTTP settings ----
USER_AGENT = "findbyusername_ossint/1.0 (+https://github.com/your-username)"
CONCURRENCY = 8
TIMEOUT = 20
RETRIES = 2
BACKOFF = 1.5


def timestamp_now_iso():
    return datetime.now(tzlocal()).isoformat()


async def fetch(session, method, url):
    for attempt in range(RETRIES + 1):
        try:
            async with session.request(method, url, allow_redirects=True) as resp:
                text = await resp.text(errors="ignore")
                return resp.status, text
        except asyncio.TimeoutError:
            if attempt < RETRIES:
                await asyncio.sleep(BACKOFF * (attempt + 1))
                continue
            return None, None
        except aiohttp.ClientError:
            return None, None
    return None, None


def heuristics_exists(platform_key, status, text):
    """
    Apply simple heuristics for platforms which sometimes return 200 for non-existent users.
    Extend this mapping as needed for more accuracy.
    """
    if status is None:
        return None, "request_failed"
    if status == 404:
        return False, ""
    if status == 200:
        # Default: assume exists, but check some platform-specific markers
        if platform_key == "github":
            if "Page not found" in text or "Not Found" in text:
                return False, "github_not_found_page"
        if platform_key == "medium":
            if "Page Not Found" in text:
                return False, "medium_not_found"
        if platform_key == "instagram":
            if "Sorry, this page isn't available." in text:
                return False, "instagram_not_found"
        # Add more checks for other platforms here...
        return True, ""
    if status in (301, 302):
        # Redirect likely to a homepage -> might exist or be handled differently
        return True, "redirect"
    if status in (403,):
        return None, "forbidden"
    if status in (429,):
        return None, "rate_limited"
    return None, f"status_{status}"


async def check_username(session, sem, username, platform_key, url_template):
    url = url_template.format(username=username)
    async with sem:
        status, text = await fetch(session, "GET", url)
    exists, note = heuristics_exists(platform_key, status, text)
    return {
        "username": username,
        "platform": platform_key,
        "url": url,
        "http_status": status,
        "exists": exists,
        "note": note,
        "checked_at": timestamp_now_iso()
    }


async def run_checks(usernames, platforms, concurrency, output_format, output_path):
    sem = asyncio.Semaphore(concurrency)
    connector = aiohttp.TCPConnector(limit_per_host=concurrency)
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    headers = {"User-Agent": USER_AGENT}

    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
        tasks = []
        for username in usernames:
            for key, tpl in platforms.items():
                tasks.append(check_username(session, sem, username, key, tpl))

        results = []
        for fut in tqdm.asyncio.as_completed(tasks, desc="Checking", total=len(tasks)):
            res = await fut
            results.append(res)

    # Save output
    if output_format == "json":
        async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        # csv
        fieldnames = ["username", "platform", "url", "http_status", "exists", "note", "checked_at"]
        async with aiofiles.open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(await f.__anext__(), fieldnames=fieldnames)  # fallback for aiosfiles
            # aiosfiles doesn't support csv writer easily; write manually
            header = ",".join(fieldnames) + "\n"
            await f.write(header)
            for row in results:
                # convert None to empty string
                line = ",".join(str(row.get(k, "")).replace(",", " ") for k in fieldnames) + "\n"
                await f.write(line)

    return results


def load_usernames_from_file(path):
    with open(path, "r", encoding="utf-8") as fh:
        names = [line.strip() for line in fh if line.strip()]
    return names


def parse_args():
    parser = argparse.ArgumentParser(description="findbyusername_ossint — check username across platforms")
    parser.add_argument("--username", "-u", help="single username to check")
    parser.add_argument("--input", "-i", help="file with usernames (one per line)")
    parser.add_argument("--output", "-o", default="results.json", help="output file (json or csv)")
    parser.add_argument("--format", "-f", default="json", choices=["json", "csv"], help="output format")
    parser.add_argument("--concurrency", "-c", type=int, default=CONCURRENCY, help="concurrency limit")
    return parser.parse_args()


def main():
    args = parse_args()
    if not (args.username or args.input):
        print("Provide --username or --input <file>")
        return

    usernames = []
    if args.username:
        usernames = [args.username.strip()]
    if args.input:
        usernames += load_usernames_from_file(args.input)

    # dedupe
    usernames = list(dict.fromkeys(usernames))

    # run
    results = asyncio.run(run_checks(usernames, PLATFORMS, args.concurrency, args.format, args.output))
    print(f"Done. Checked {len(usernames)} username(s). Results saved to {args.output}")


if __name__ == "__main__":
    main()
