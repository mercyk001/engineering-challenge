"""
Centralized selectors and small heuristics for kenyalaw.org

"""
INDEX_SELECTORS = [
    "main a[href]",
    "article a[href]",
    ".content a[href]",
    ".document-list a[href]",
    ".latest-news a[href]",
    "a[href*='/caselaw/']",
]

TITLE_SELECTORS = ["h1", 'meta[property="og:title"]', 'meta[name="og:title"]']
SUMMARY_SELECTORS = [".summary", ".headnote", "#summary", ".case-summary", "article p", "main p"]
PDF_SELECTOR = "a[href$='.pdf']"