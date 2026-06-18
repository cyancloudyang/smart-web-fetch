"""
searx_pro_engine.py v4
Multi-round distributed SearX search with early termination.

Usage:
  python3 searx_pro_engine.py "<ZH_R1>;<ZH_R2>;<ZH_R3>" "<EN_R1>;<EN_R2>;<EN_R3>"
  # Semicolons separate search rounds (R1/R2/R3). Unused rounds can be omitted.
  # Examples:
  python3 searx_pro_engine.py "玲珑瓷 景德镇" "linglong porcelain Jingdezhen"
  python3 searx_pro_engine.py "玲珑瓷 景德镇;玲珑杯 价格;景德镇陶瓷" "linglong porcelain;reticulated ceramic;Jingdezhen industry"
"""

import requests
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

# ============================================================
# Noise filter configuration
# ============================================================

DOMAIN_BLACKLIST_PATTERNS = [
    "searx.", "ooglester.com", "searx.be", "searx.work",
    "ononoki.org", "techaro.lol", "paulgo.page",
]

GOVERNMENT_DOMAIN_PATTERNS = [
    "gouv.fr", "gov.uk", "gov.au", "gov.cn", "gov.jp",
    "gov.tw", "gov.hk", "gov.sg", "service-public.fr",
]

STATIC_EXTENSIONS = frozenset([
    ".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".css", ".js", ".woff", ".woff2", ".ttf", ".eot", ".mp4"
])

PATH_BLACKLIST = [
    "/preferences", "/about", "/donate", "/stats", "/info/",
    "/favicon.ico", "/robots.txt", "/search", "/config",
    "/privacy", "/impressum", "/spenden", "/status", "/support",
    "/contact", "/captcha", "/health", "/metrics"
]

TITLE_BLACKLIST = {
    "Preferences", "About", "Donate", "Stats", "SearXNG",
    "Search", "Settings", "Help", "Documentation",
    "Oh noes!", "Anubis", "Go home",
    "Contact instance maintainer", "Impressum", "Privacy policy",
    "Spenden", "Status", "CELPHASE", "Techaro"
}

TITLE_PREFIX_BLACKLIST = [
    r"^Image \d+",
    r"^Sorry",
    r"^Internal Server Error",
    r"^No results",
    r"^Page \d+ of",
]

_TITLE_PREFIX_RE = re.compile("|".join(TITLE_PREFIX_BLACKLIST), re.IGNORECASE)

ERROR_TITLE_KEYWORDS = [
    "no results", "sorry", "internal server error",
    "captcha", "suspended", "blocked", "access denied",
    "error", "403", "404", "500", "502", "503",
    "too many requests", "rate limit", "service unavailable"
]

# Round weight configuration: later rounds get lower weight
ROUND_WEIGHTS = {
    0: 1.0,   # R1 core
    1: 0.8,   # R2 expand
    2: 0.6,   # R3 fallback
}

# R3 only uses non-EN nodes to reduce pressure
R3_SKIP_EN_NODES = True

# Early termination threshold: skip remaining rounds if enough results
EARLY_STOP_THRESHOLD = 10


def get_node_pool():
    """Fetch candidate nodes from searx.space, filter by TLS grade and response time."""
    url = "https://searx.space/data/instances.json"
    try:
        data = requests.get(url, timeout=15).json().get("instances", {})
        us_gb = []
        other = []
        for base_url, info in data.items():
            tls_grade = info.get("tls", {}).get("grade", "")
            if tls_grade not in ("A+", "A"):
                continue
            timing = info.get("timing", {}).get("initial", {}).get("all", {}).get("value", 99)
            if timing > 5.0:
                continue
            if info.get("network_type") == "tor":
                continue
            issuer_country = info.get("tls", {}).get("certificate", {}).get("issuer", {}).get("countryName", "")
            if issuer_country in ("US", "GB") or ".us" in base_url or ".uk" in base_url:
                us_gb.append((base_url, timing))
            else:
                other.append((base_url, timing))

        us_gb.sort(key=lambda x: x[1])
        other.sort(key=lambda x: x[1])
        return [n[0] for n in us_gb[:5]], [n[0] for n in other[:8]]
    except:
        return (
            ["https://paulgo.io/", "https://searx.dresden.network/"],
            ["https://search.ononoki.org/", "https://searx.work/"]
        )


def parse_markdown_results(md_text):
    """Extract search result links from Jina-returned Markdown text."""
    results = []
    pattern = r"\[([^\]]+)\]\((https?://[^\)]+)\)"
    matches = re.findall(pattern, md_text)

    for title, url in matches:
        title = title.strip()
        url = url.strip()

        if "jina.ai" in url:
            continue
        url_domain = urlparse(url).netloc.lower()
        if any(pat in url_domain for pat in DOMAIN_BLACKLIST_PATTERNS):
            continue
        if "searx" in url.lower():
            continue
        url_path = urlparse(url).path.lower()
        if any(url_path.endswith(ext) for ext in STATIC_EXTENSIONS):
            continue
        parsed_path = urlparse(url).path
        if any(parsed_path.startswith(p) for p in PATH_BLACKLIST):
            continue
        if title in TITLE_BLACKLIST:
            continue
        if _TITLE_PREFIX_RE.search(title):
            continue
        title_lower = title.lower()
        if any(kw in title_lower for kw in ERROR_TITLE_KEYWORDS):
            continue
        if len(title) < 3 or title.isdigit():
            continue
        if any(pat in url_domain for pat in GOVERNMENT_DOMAIN_PATTERNS):
            continue
        if title.count("›") >= 2 or title.count("|") >= 3:
            continue

        results.append({"title": title, "url": url})

    return results


def proxy_search(node_url, query, language="all", weight=1.0):
    """Fetch search results from a SearX node via Jina proxy."""
    search_link = f"{node_url}search?q={query.replace(' ', '+')}&language={language}"
    proxy_url = f"https://r.jina.ai/{search_link}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        r = requests.get(proxy_url, headers=headers, timeout=12)
        if r.status_code != 200:
            return [], weight
        body = r.text
        body_lower = body[:2000].lower()
        zero_result_signals = [
            "sorry! no results were found",
            "no results were found",
            "no results found",
            "internal server error",
            "administrator has misconfigured",
        ]
        if any(sig in body_lower for sig in zero_result_signals):
            return [], weight
        if len(body.strip()) < 500:
            return [], weight
        return parse_markdown_results(body), weight
    except:
        return [], weight


def _extract_keywords(query_text):
    """Extract keywords and bigrams from query text for relevance checking."""
    stop_words = {
        "的", "和", "与", "及", "了", "在", "是", "有", "等", "这", "那",
        "the", "a", "an", "of", "in", "for", "and", "or", "with", "to", "is", "are",
    }
    keywords = set()
    for w in re.split(r"[\s,，、；;]+", query_text):
        w = w.strip().lower()
        if len(w) >= 2 and w not in stop_words:
            keywords.add(w)
    bigrams = set()
    words = query_text.lower().split()
    for i in range(len(words) - 1):
        if words[i] not in stop_words and words[i + 1] not in stop_words:
            bigrams.add(f"{words[i]} {words[i + 1]}")
    return keywords, bigrams


def run_pro_search(q_zh, q_en):
    """
    Multi-round distributed search with early termination.

    v4 changes:
    - Accepts semicolon-separated multi-round queries (R1;R2;R3)
    - Early termination: skips R2/R3 if enough results found
    - Weight degradation across rounds (1.0 -> 0.8 -> 0.6)
    - R3 skips EN nodes to reduce SearX pressure
    - Keyword extraction covers all rounds for broader relevance matching
    """
    us_gb, fast_ap = get_node_pool()
    all_results = {}

    zh_rounds = [q.strip() for q in q_zh.split(";") if q.strip()]
    en_rounds = [q.strip() for q in q_en.split(";") if q.strip()]

    max_rounds = max(len(zh_rounds), len(en_rounds))
    zh_rounds += [""] * (max_rounds - len(zh_rounds))
    en_rounds += [""] * (max_rounds - len(en_rounds))

    all_query_text = " ".join(zh_rounds + en_rounds)
    query_keywords, query_bigrams = _extract_keywords(all_query_text)

    def collect_results(result_futures):
        for f in result_futures:
            results, weight = f.result()
            for idx, res in enumerate(results):
                url = res["url"].rstrip("/")
                score = weight * (1.0 / (idx + 10))
                if url not in all_results:
                    all_results[url] = {
                        "title": res["title"],
                        "hits": 1,
                        "score": score,
                        "original_url": res["url"],
                        "jina_url": f"https://r.jina.ai/{res['url']}"
                    }
                else:
                    all_results[url]["hits"] += 1
                    all_results[url]["score"] += (score + 1.5)

    for round_idx in range(max_rounds):
        q_z = zh_rounds[round_idx]
        q_e = en_rounds[round_idx]
        if not q_z and not q_e:
            continue
        base_weight = ROUND_WEIGHTS.get(round_idx, 0.6)
        if round_idx >= 2 and R3_SKIP_EN_NODES:
            en_nodes = []
        else:
            en_nodes = us_gb

        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = []
            for n in en_nodes:
                if q_e:
                    futures.append(executor.submit(proxy_search, n, q_e, "en-US", base_weight * 1.5))
                if q_z:
                    futures.append(executor.submit(proxy_search, n, q_z, "all", base_weight))
            for n in fast_ap:
                if q_z:
                    futures.append(executor.submit(proxy_search, n, q_z, "all", base_weight))
            collect_results(futures)

        if len(all_results) >= EARLY_STOP_THRESHOLD and round_idx < max_rounds - 1:
            break

    filtered_results = []
    for item in all_results.values():
        title_lower = item["title"].lower()
        url_lower = item["original_url"].lower()
        domain = urlparse(item["original_url"]).netloc.lower()
        bigram_hit = any(bg in title_lower for bg in query_bigrams)
        keyword_hit = any(kw in title_lower or kw in domain or kw in url_lower for kw in query_keywords)
        if bigram_hit or keyword_hit:
            filtered_results.append(item)

    sorted_res = sorted(filtered_results, key=lambda x: x["score"], reverse=True)
    return sorted_res[:15]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: python3 searx_pro_engine.py <ZH_QUERY> <EN_QUERY>"
                   "\nSeparate multiple rounds with semicolons: R1;R2;R3"
        }))
        sys.exit(1)
    q_zh, q_en = sys.argv[1], sys.argv[2]
    t0 = time.time()
    final_15 = run_pro_search(q_zh, q_en)
    elapsed = round(time.time() - t0, 1)

    zh_rounds = len([q for q in q_zh.split(";") if q.strip()])
    en_rounds = len([q for q in q_en.split(";") if q.strip()])

    print(json.dumps({
        "meta": {
            "version": 4,
            "rounds_configured": max(zh_rounds, en_rounds),
            "effective_results": len(final_15),
            "elapsed_sec": elapsed,
        },
        "results": final_15
    }, indent=2, ensure_ascii=False))