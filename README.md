# findbyusername_ossint

# 🔎 findbyusername_ossint

**Async OSINT tool** to quickly check whether a username exists across common platforms.  
Useful for footprinting, digital profiling, and collecting public presence signals. Outputs results as JSON and CSV for analysis.

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
