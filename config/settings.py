"""
Application settings (small and overridable with environment variables)
"""
import os

DEFAULTS = {
    "BASE_URL": "https://www.kenyalaw.org",
    "INDEX_PATH": "/caselaw",
    "MAX_CONCURRENCY": 4,
    "REQUEST_DELAY": 0.5,
    "REQUEST_TIMEOUT": 20,
    "DEFAULT_USER_AGENT": "KenyaLawScraper/1.0 (mailto:you@example.com)",
    "RESULTS_DIR": "data",
}

SETTINGS = {**DEFAULTS}



for k in DEFAULTS:
    SETTINGS[k] = os.environ.get(k, DEFAULTS[k])