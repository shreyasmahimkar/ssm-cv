"""
randstaddigital_job_matcher.py — On-demand job-board scanner that ranks live
postings against Shreyas's resume, WITHOUT a headless browser.

Built for Randstad Digital (auto-uses their daily job sitemap) but works on any
board that embeds JobPosting JSON-LD: pass an XML sitemap or a single posting.

How it works
------------
Most job boards (Randstad, Greenhouse, Lever, LinkedIn, company career pages)
embed a Google-for-Jobs ``JobPosting`` block as server-rendered JSON-LD. That
means a plain HTTP GET returns the full posting (title, location, salary,
employment type, description) even when the listing UI itself is JavaScript.
This script:

  1. Resolves the input URL into a set of individual job-page URLs
     (a single posting, an XML sitemap, or a known site adapter).
  2. Pre-filters those URLs by slug keywords so we only fetch plausibly
     relevant pages (avoids hammering 900 listings).
  3. Fetches each page, parses its JobPosting JSON-LD.
  4. Scores the title + description against resume keywords and prints a
     ranked shortlist.

Usage
-----
  python randstaddigital_job_matcher.py <url> [--top 15] [--min-score 4]
        [--limit 60] [--require "Randstad Digital"] [--markdown]
        [--json out.json] [--refresh-resume]

Examples
--------
  # Scan all live Randstad Digital postings (auto-uses their sitemap):
  python randstaddigital_job_matcher.py \
      https://www.randstadusa.com/jobs/s-randstad-digital/ \
      --require "Randstad Digital" --markdown

  # Score one specific posting:
  python randstaddigital_job_matcher.py \
      https://www.randstadusa.com/jobs/4/1336678/quantitative-analytics-specialist_charlotte/

  # Any other board's XML sitemap:
  python randstaddigital_job_matcher.py https://boards.greenhouse.io/example/sitemap.xml
"""

import argparse
import json
import re
import sys
import time
from urllib.parse import urlparse

import requests

try:
    from resume_parser import get_resume_data
except Exception:  # pragma: no cover - resume_parser is in the same repo
    get_resume_data = None

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
TIMEOUT = 15

# ---------------------------------------------------------------------------
# Scoring vocabulary
# ---------------------------------------------------------------------------

# Strong role-title signals (matched anywhere, extra boost if in the title).
ROLE_TERMS = {
    "data scientist": 4,
    "research scientist": 4,
    "applied scientist": 4,
    "ai researcher": 4,
    "ai research": 3,
    "machine learning engineer": 4,
    "ml engineer": 4,
    "data science": 3,
    "quantitative analyst": 3,
    "quantitative analytics": 3,
    "quant ": 2,
    "statistician": 3,
    "ai engineer": 3,
    "lead ai": 4,
    "principal data": 4,
}

# Core competency signals.
DOMAIN_TERMS = {
    "machine learning": 3,
    "deep learning": 3,
    "large language model": 3,
    " llm": 3,
    "generative ai": 3,
    "genai": 3,
    "causal inference": 3,
    "multi-agent": 3,
    "multi agent": 3,
    "reinforcement learning": 2,
    "natural language processing": 2,
    " nlp": 2,
    "time series": 2,
    "time-series": 2,
    "forecasting": 2,
    "predictive model": 2,
    "bayesian": 2,
    "clustering": 1,
    "mlops": 2,
    "recommendation": 1,
    "computer vision": 1,
    "statistical model": 2,
    "experimentation": 1,
    "a/b test": 1,
}

# Tooling signals.
TOOL_TERMS = {
    "python": 2,
    "pytorch": 2,
    "tensorflow": 2,
    "scikit": 1,
    " spark": 2,
    "hadoop": 1,
    "aws": 1,
    "athena": 1,
    " emr": 1,
    "gcp": 1,
    "vertex ai": 2,
    "sagemaker": 1,
    "databricks": 1,
    "snowflake": 1,
    " sql": 1,
    "scala": 1,
    "docker": 1,
    "kubernetes": 1,
    "airflow": 1,
}

# URL-slug pre-filter: only fetch pages whose slug hints at a relevant role.
SLUG_KEYWORDS = [
    "data-scien", "data-engineer", "machine-learning", "ml-engineer",
    "ai-engineer", "ai-research", "research-scien", "applied-scien",
    "data-analytics", "analytics", "quantitative", "quant-", "statistic",
    "data-architect", "nlp", "artificial-intelligence", "deep-learning",
    "ai-ml", "ml-ops", "mlops", "data-science",
]


def build_keyword_weights(extra_keywords=None, refresh_resume=False):
    """Merge static vocab with skills pulled from the resume."""
    weights = {}
    for table in (ROLE_TERMS, DOMAIN_TERMS, TOOL_TERMS):
        weights.update(table)

    # Pull concrete skill terms straight from the resume so the vocabulary
    # tracks whatever is in the master doc.
    if get_resume_data is not None:
        try:
            resume = get_resume_data(force_refresh=refresh_resume)
        except Exception as exc:
            print(f"[warn] could not load resume skills: {exc}", file=sys.stderr)
            resume = None
        if resume:
            for skill_list in (resume.get("skills") or {}).values():
                for skill in skill_list:
                    # Use the head term before any parenthetical/qualifier.
                    term = re.split(r"[(/,]", skill)[0].strip().lower()
                    if 3 <= len(term) <= 30:
                        weights.setdefault(term, 1)

    for kw in extra_keywords or []:
        weights[kw.strip().lower()] = max(weights.get(kw.strip().lower(), 0), 3)

    return weights


# ---------------------------------------------------------------------------
# Fetching & URL resolution
# ---------------------------------------------------------------------------

def http_get(url):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.text


# Known adapters: map a human-facing board URL to its job sitemap.
SITE_ADAPTERS = {
    "randstadusa.com": "https://www.randstadusa.com/sitemaps/us/sitemap-jobs.xml",
}


def resolve_job_urls(url, limit_discovery=5000):
    """Return a list of individual job-page URLs from the given input URL."""
    host = urlparse(url).netloc.lower().replace("www.", "")
    looks_like_sitemap = url.endswith(".xml") or "sitemap" in url.lower()

    # A specific posting page: /jobs/<...>/<slug>/ where slug has a word char.
    # Slugs use hyphens/underscores (e.g. senior-data-engineer_malvern).
    is_single_job = bool(re.search(r"/jobs?/.+/[a-z0-9][a-z0-9_-]*/?$", url, re.I)) and not looks_like_sitemap

    if is_single_job and host not in ("",):
        # Treat as a single posting unless it's clearly a listing root.
        if not url.rstrip("/").endswith(("/jobs", "/job", "s-randstad-digital")):
            return [url.rstrip("/") + "/"] if not url.endswith("/") else [url]

    if not looks_like_sitemap and host in SITE_ADAPTERS:
        url = SITE_ADAPTERS[host]
        looks_like_sitemap = True

    if looks_like_sitemap:
        return _expand_sitemap(url, limit_discovery)

    # Fallback: try to read JSON-LD straight off whatever page this is.
    return [url]


def _expand_sitemap(url, limit, _depth=0):
    """Recursively expand a sitemap or sitemap-index into job URLs."""
    if _depth > 3:
        return []
    try:
        xml = http_get(url)
    except Exception as exc:
        print(f"[warn] could not fetch sitemap {url}: {exc}", file=sys.stderr)
        return []

    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)
    is_index = "<sitemapindex" in xml.lower()

    if is_index:
        # Prefer child sitemaps that look job-related.
        children = [l for l in locs if any(k in l.lower() for k in ("job", "sitemap-jobs"))] or locs
        out = []
        for child in children:
            out.extend(_expand_sitemap(child, limit, _depth + 1))
            if len(out) >= limit:
                break
        return out[:limit]

    # Leaf sitemap: keep only URLs that look like job postings.
    jobs = [l for l in locs if "/job" in l.lower()]
    return (jobs or locs)[:limit]


def prefilter_urls(urls, keywords=SLUG_KEYWORDS):
    """Keep only URLs whose slug suggests a relevant role (case-insensitive)."""
    kept = [u for u in urls if any(k in u.lower() for k in keywords)]
    # If the slugs carry no hints at all (some boards use opaque ids), don't
    # over-prune — fall back to the full list and let scoring decide.
    return kept if kept else urls


# ---------------------------------------------------------------------------
# JSON-LD parsing
# ---------------------------------------------------------------------------

LD_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.S | re.I,
)


def _iter_jobposting_nodes(data):
    """Yield JobPosting dicts from arbitrary JSON-LD shapes (@graph, lists)."""
    if isinstance(data, list):
        for item in data:
            yield from _iter_jobposting_nodes(item)
    elif isinstance(data, dict):
        if "@graph" in data:
            yield from _iter_jobposting_nodes(data["@graph"])
        t = data.get("@type")
        types = t if isinstance(t, list) else [t]
        if "JobPosting" in types:
            yield data


def parse_jobpostings(html, source_url):
    jobs = []
    for block in LD_RE.findall(html):
        block = block.strip()
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        for node in _iter_jobposting_nodes(data):
            jobs.append(_normalize_job(node, source_url))
    return jobs


def _job_id_from_url(url):
    """Pull the posting id from a Randstad-style /jobs/<div>/<id>/<slug>/ URL."""
    m = re.search(r"/jobs?/[^/]+/([^/]+)/", url or "")
    return m.group(1) if m else ""


def _normalize_job(node, source_url):
    desc = re.sub(r"<[^>]+>", " ", node.get("description", "") or "")
    desc = re.sub(r"\s+", " ", desc).strip()
    url = node.get("url") or source_url
    return {
        "job_id": _job_id_from_url(url),
        "title": (node.get("title") or "").strip(),
        "location": _fmt_location(node.get("jobLocation")),
        "employment_type": _fmt_employment(node.get("employmentType")),
        "salary": _fmt_salary(node.get("baseSalary")),
        "date_posted": node.get("datePosted", ""),
        "valid_through": node.get("validThrough", ""),
        "organization": (node.get("hiringOrganization") or {}).get("name", "")
        if isinstance(node.get("hiringOrganization"), dict) else "",
        "description": desc,
        "url": url,
    }


def _fmt_location(loc):
    if isinstance(loc, list):
        return "; ".join(filter(None, (_fmt_location(x) for x in loc)))
    if isinstance(loc, dict):
        addr = loc.get("address", {})
        if isinstance(addr, dict):
            parts = [addr.get("addressLocality"), addr.get("addressRegion")]
            return ", ".join([p for p in parts if p])
    return ""


def _fmt_employment(et):
    if isinstance(et, str) and et.strip().startswith("["):
        try:
            et = json.loads(et)
        except json.JSONDecodeError:
            pass
    if isinstance(et, list):
        return ", ".join(str(x).replace("_", " ").title() for x in et)
    if isinstance(et, str):
        return et.replace("_", " ").title()
    return ""


def _fmt_salary(sal):
    if not isinstance(sal, dict):
        return ""
    cur = sal.get("currency", "")
    val = sal.get("value", {})
    if not isinstance(val, dict):
        return ""
    unit = (val.get("unitText") or "").lower()
    lo, hi, exact = val.get("minValue"), val.get("maxValue"), val.get("value")
    sym = "$" if cur in ("USD", "$") else (cur + " ")
    per = {"hour": "/hr", "year": "/yr", "month": "/mo", "week": "/wk", "day": "/day"}.get(unit, "")
    if lo is not None and hi is not None:
        return f"{sym}{lo:g}–{hi:g}{per}"
    if exact is not None:
        return f"{sym}{exact:g}{per}"
    return ""


# ---------------------------------------------------------------------------
# Visa sponsorship
# ---------------------------------------------------------------------------
# Shreyas requires sponsorship, so postings that rule it out are filtered.
# Randstad usually omits this from the page text, so detection is best-effort;
# the confirmed-blocklist file (no_sponsor_ids.txt) is the reliable backstop.

NO_SPONSOR_PHRASES = [
    "no sponsorship", "without sponsorship", "no visa sponsorship",
    "not provide sponsorship", "unable to provide sponsorship",
    "does not provide sponsorship", "not able to provide sponsorship",
    "will not sponsor", "cannot sponsor", "can not sponsor", "do not sponsor",
    "not able to sponsor", "unable to sponsor", "not offer sponsorship",
    "not be able to sponsor", "no c2c", "no corp to corp", "no corp-to-corp",
    "w2 only", "no third party", "no third-party",
    "must be a us citizen", "must be a u.s. citizen", "us citizens only",
    "u.s. citizens only", "citizenship is required", "requires us citizenship",
    "us citizen or green card", "citizen or permanent resident",
    "green card holder", "gc or usc", "usc/gc", "usc or gc",
    "active security clearance", "security clearance required",
]
YES_SPONSOR_PHRASES = [
    "sponsorship available", "will sponsor", "open to sponsorship",
    "visa sponsorship is available", "offer sponsorship", "h1b", "h-1b",
    "willing to sponsor",
]


def sponsorship_signal(text):
    """Best-effort read of a posting's sponsorship stance: 'no' | 'yes' | 'unclear'."""
    t = text.lower()
    if any(p in t for p in NO_SPONSOR_PHRASES):
        return "no"
    if any(p in t for p in YES_SPONSOR_PHRASES):
        return "yes"
    return "unclear"


def load_no_sponsor_ids(path):
    """Read confirmed no-sponsor job ids (one per line; '#' comments allowed)."""
    ids = set()
    try:
        with open(path) as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                if line:
                    ids.add(line)
    except FileNotFoundError:
        pass
    return ids


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_job(job, weights):
    title = job["title"].lower()
    text = (job["title"] + " . " + job["description"]).lower()
    score = 0
    best = {}  # stripped term -> best per-hit weight (dedupes " sql" vs "sql")
    for term, w in weights.items():
        if term in text:
            hit = w
            if term in title:  # title mentions count double
                hit += w
            score += hit
            key = term.strip()
            best[key] = max(best.get(key, 0), hit)
    matched = sorted(best.items(), key=lambda x: -x[1])
    job["score"] = score
    job["matched"] = [m[0] for m in matched[:8]]
    return job


# ---------------------------------------------------------------------------
# Orchestration & CLI
# ---------------------------------------------------------------------------

def run(url, top, min_score, limit, require, extra_keywords, refresh_resume, delay,
        no_sponsor_ids=None, keep_no_sponsor=False, exclude_ids=None, extra_slugs=None):
    weights = build_keyword_weights(extra_keywords, refresh_resume)
    no_sponsor_ids = no_sponsor_ids or set()
    exclude_ids = exclude_ids or set()

    print(f"[*] Resolving job URLs from: {url}", file=sys.stderr)
    all_urls = resolve_job_urls(url)
    print(f"[*] Discovered {len(all_urls)} candidate URL(s).", file=sys.stderr)

    slug_kws = SLUG_KEYWORDS + list(extra_slugs or [])
    candidates = prefilter_urls(all_urls, slug_kws)
    if len(candidates) != len(all_urls):
        print(f"[*] Slug pre-filter kept {len(candidates)} relevant URL(s).", file=sys.stderr)
    candidates = candidates[:limit]
    print(f"[*] Fetching up to {len(candidates)} page(s)...", file=sys.stderr)

    results = []
    excluded = []  # (title, job_id, reason)
    seen_skipped = 0
    seen = set()
    for i, job_url in enumerate(candidates, 1):
        try:
            html = http_get(job_url)
        except Exception as exc:
            print(f"  [skip] {job_url} ({exc})", file=sys.stderr)
            continue
        for job in parse_jobpostings(html, job_url):
            key = (job["title"], job["location"])
            if key in seen:
                continue
            if require and require.lower() not in (job["description"] + " " + job["organization"]).lower():
                continue
            seen.add(key)

            # Already surfaced in a previous run — skip silently (just count).
            if job["job_id"] in exclude_ids:
                seen_skipped += 1
                continue

            # Sponsorship stance: confirmed blocklist wins, else best-effort text scan.
            if job["job_id"] in no_sponsor_ids:
                job["sponsorship"] = "no"
                job["sponsorship_source"] = "confirmed"
            else:
                job["sponsorship"] = sponsorship_signal(job["title"] + " . " + job["description"])
                job["sponsorship_source"] = "posting text"

            if job["sponsorship"] == "no" and not keep_no_sponsor:
                excluded.append((job["title"], job["job_id"], job["sponsorship_source"]))
                continue

            results.append(score_job(job, weights))
        if delay:
            time.sleep(delay)

    if seen_skipped:
        print(f"[*] Skipped {seen_skipped} already-seen posting(s) (exclude list).", file=sys.stderr)
    if excluded:
        print(f"[*] Excluded {len(excluded)} no-sponsorship posting(s):", file=sys.stderr)
        for title, jid, src in excluded:
            print(f"      - {title} (id {jid}, {src})", file=sys.stderr)

    results = [r for r in results if r["score"] >= min_score]
    results.sort(key=lambda j: -j["score"])
    return results[:top]


def print_report(jobs):
    if not jobs:
        print("\nNo postings cleared the score threshold. Try lowering --min-score "
              "or widening the search.\n")
        return
    print(f"\n{'='*70}\n  {len(jobs)} TOP MATCHES (ranked by fit)\n{'='*70}")
    for rank, j in enumerate(jobs, 1):
        print(f"\n#{rank}  [{j['score']}]  {j['title']}")
        meta = " · ".join(filter(None, [j["location"], j["employment_type"], j["salary"]]))
        if meta:
            print(f"     {meta}")
        line = f"     job id: {j['job_id']}" if j["job_id"] else "     "
        if j["valid_through"]:
            line += f"   ·   open through {j['valid_through']}"
        print(line)
        if j["matched"]:
            print(f"     matched: {', '.join(j['matched'])}")
        print(f"     {j['url']}")
    print()


def print_markdown(jobs):
    """Emit a ready-to-paste markdown table: #, Role, Location, Comp, Job ID, Link."""
    if not jobs:
        print("\n_No postings cleared the score threshold._\n")
        return
    print("\n| # | Role | Location | Comp | Type | Job ID | Link |")
    print("|---|------|----------|------|------|--------|------|")
    for rank, j in enumerate(jobs, 1):
        link = f"[open]({j['url']})" if j["url"] else ""
        jid = f"**{j['job_id']}**" if j["job_id"] else ""
        cells = [str(rank), j["title"], j["location"] or "—", j["salary"] or "—",
                 j["employment_type"] or "—", jid, link]
        print("| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |")
    print()


def main(argv=None):
    p = argparse.ArgumentParser(description="Rank live job postings against the resume.")
    p.add_argument("url", help="A board URL, XML sitemap, or single job posting URL.")
    p.add_argument("--top", type=int, default=15, help="Max matches to show (default 15).")
    p.add_argument("--min-score", type=int, default=4, help="Minimum fit score (default 4).")
    p.add_argument("--limit", type=int, default=60, help="Max job pages to fetch (default 60).")
    p.add_argument("--require", default=None,
                   help='Only keep postings whose text contains this string (e.g. "Randstad Digital").')
    p.add_argument("--keywords", default=None,
                   help="Comma-separated extra high-weight keywords to boost.")
    p.add_argument("--delay", type=float, default=0.15, help="Politeness delay between fetches (s).")
    p.add_argument("--markdown", action="store_true", help="Print results as a markdown table.")
    p.add_argument("--no-sponsor-file", default="no_sponsor_ids.txt",
                   help="File of confirmed no-sponsorship job ids to exclude (default no_sponsor_ids.txt).")
    p.add_argument("--keep-no-sponsor", action="store_true",
                   help="Do NOT filter out roles flagged as offering no visa sponsorship.")
    p.add_argument("--exclude-file", default="seen_ids.txt",
                   help="File of already-seen job ids to skip (default seen_ids.txt).")
    p.add_argument("--mark-seen", action="store_true",
                   help="Append this run's matched job ids to --exclude-file so they don't recur.")
    p.add_argument("--extra-slugs", default=None,
                   help="Comma-separated extra URL-slug keywords to widen the pre-filter.")
    p.add_argument("--refresh-resume", action="store_true", help="Re-fetch resume from Google Docs.")
    p.add_argument("--json", dest="json_out", default=None, help="Also write full results to this JSON file.")
    args = p.parse_args(argv)

    extra = [k for k in (args.keywords or "").split(",") if k.strip()]
    extra_slugs = [s.strip().lower() for s in (args.extra_slugs or "").split(",") if s.strip()]
    no_sponsor_ids = load_no_sponsor_ids(args.no_sponsor_file)
    exclude_ids = load_no_sponsor_ids(args.exclude_file)  # same format (id per line)
    jobs = run(args.url, args.top, args.min_score, args.limit, args.require,
               extra, args.refresh_resume, args.delay,
               no_sponsor_ids=no_sponsor_ids, keep_no_sponsor=args.keep_no_sponsor,
               exclude_ids=exclude_ids, extra_slugs=extra_slugs)
    if args.markdown:
        print_markdown(jobs)
    else:
        print_report(jobs)

    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(jobs, f, indent=2)
        print(f"[*] Wrote {len(jobs)} results to {args.json_out}", file=sys.stderr)

    if args.mark_seen and jobs:
        new_ids = [j["job_id"] for j in jobs if j["job_id"]]
        with open(args.exclude_file, "a") as f:
            for jid in new_ids:
                f.write(f"{jid}\n")
        print(f"[*] Marked {len(new_ids)} job id(s) as seen in {args.exclude_file}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
