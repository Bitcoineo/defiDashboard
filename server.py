#!/usr/bin/env python3
"""DeFi Protocol Dashboard — API proxy server with caching."""

import json
import os
import ssl
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8000
CACHE_TTL = 300  # 5 minutes
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------
_cache: dict[str, dict] = {}


def cache_get(key: str):
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL:
        return entry["data"]
    return None


def cache_set(key: str, data):
    _cache[key] = {"data": data, "ts": time.time()}


# ---------------------------------------------------------------------------
# Upstream fetcher
# ---------------------------------------------------------------------------
try:
    import certifi
    _ssl_ctx = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _ssl_ctx = ssl.create_default_context()


def fetch_json(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# Data transformers
# ---------------------------------------------------------------------------

YIELD_FIELDS = (
    "pool", "project", "symbol", "chain",
    "apy", "apyBase", "apyReward",
    "tvlUsd", "stablecoin",
)


def transform_protocols(data: list) -> list:
    valid = [p for p in data
             if isinstance(p.get("tvl"), (int, float))
             and p.get("category") != "CEX"]
    valid.sort(key=lambda p: p["tvl"], reverse=True)
    return valid[:20]


def transform_chains(data: list) -> list:
    valid = [c for c in data if isinstance(c.get("tvl"), (int, float))]
    valid.sort(key=lambda c: c["tvl"], reverse=True)
    return valid


def transform_yields(data: dict) -> list:
    pools = data.get("data", [])
    filtered = [
        {k: p.get(k) for k in YIELD_FIELDS}
        for p in pools
        if isinstance(p.get("tvlUsd"), (int, float))
        and isinstance(p.get("apy"), (int, float))
        and p["tvlUsd"] > 10_000
        and 0 < p["apy"] < 1000
        and not p.get("outlier")
    ]
    filtered.sort(key=lambda p: p["tvlUsd"], reverse=True)
    return filtered[:100]


def transform_tvl_history(data: list) -> dict:
    """Return last 30 days of total DeFi TVL plus computed stats."""
    if not data or len(data) < 2:
        return {"points": [], "tvl": 0, "change24h": 0}
    recent = data[-30:] if len(data) >= 30 else data
    tvl_now = recent[-1]["tvl"]
    tvl_prev = recent[-2]["tvl"] if len(recent) >= 2 else tvl_now
    change_pct = ((tvl_now - tvl_prev) / tvl_prev * 100) if tvl_prev else 0
    return {
        "tvl": tvl_now,
        "change24h": round(change_pct, 4),
        "points": [entry["tvl"] for entry in recent],
    }


def build_sparklines(slugs: list[str]) -> dict[str, list[float]]:
    """Fetch last 7 days of TVL for each protocol slug in parallel."""
    result: dict[str, list[float]] = {}

    def _fetch_one(slug: str):
        try:
            detail = fetch_json(f"https://api.llama.fi/protocol/{slug}", timeout=15)
            tvl = detail.get("tvl")
            if isinstance(tvl, list) and tvl:
                recent = tvl[-7:] if len(tvl) >= 7 else tvl
                return slug, [e.get("totalLiquidityUSD", 0) for e in recent]
        except Exception:
            pass
        return slug, []

    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(_fetch_one, s): s for s in slugs}
        for fut in as_completed(futures):
            slug, values = fut.result()
            result[slug] = values

    return result


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        # Quieter logs: just method + path + status
        pass

    # -- helpers ------------------------------------------------------------

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status, message):
        self.send_json({"error": message}, status)

    def serve_file(self, filepath, content_type):
        try:
            with open(filepath, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_error_json(404, "File not found")

    def proxy(self, upstream_url: str, transform=None, cache_key: str | None = None):
        key = cache_key or upstream_url
        cached = cache_get(key)
        if cached is not None:
            self.send_json(cached)
            return

        try:
            data = fetch_json(upstream_url)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            self.send_error_json(502, f"Upstream error: {exc}")
            return
        except json.JSONDecodeError:
            self.send_error_json(502, "Invalid JSON from upstream")
            return

        if transform:
            data = transform(data)

        cache_set(key, data)
        self.send_json(data)

    # -- routing ------------------------------------------------------------

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"

        if path == "/":
            self.serve_file(os.path.join(STATIC_DIR, "index.html"), "text/html; charset=utf-8")

        elif path == "/api/protocols":
            self.proxy("https://api.llama.fi/protocols", transform_protocols)

        elif path.startswith("/api/protocol/"):
            slug = path.split("/api/protocol/", 1)[1]
            if not slug or "/" in slug:
                self.send_error_json(400, "Invalid slug")
                return
            self.proxy(f"https://api.llama.fi/protocol/{slug}")

        elif path == "/api/chains":
            self.proxy("https://api.llama.fi/v2/chains", transform_chains)

        elif path == "/api/yields":
            self.proxy(
                "https://yields.llama.fi/pools",
                transform_yields,
                cache_key="yields",
            )

        elif path == "/api/sparklines":
            cached = cache_get("sparklines")
            if cached is not None:
                self.send_json(cached)
                return
            # Get protocol slugs (from cache or fresh fetch)
            protocols = cache_get("https://api.llama.fi/protocols")
            if not protocols:
                try:
                    raw = fetch_json("https://api.llama.fi/protocols")
                    protocols = transform_protocols(raw)
                    cache_set("https://api.llama.fi/protocols", protocols)
                except Exception:
                    self.send_error_json(502, "Failed to fetch protocol list")
                    return
            slugs = [p["slug"] for p in protocols]
            sparklines = build_sparklines(slugs)
            cache_set("sparklines", sparklines)
            self.send_json(sparklines)

        elif path == "/api/tvl-history":
            self.proxy(
                "https://api.llama.fi/v2/historicalChainTvl",
                transform_tvl_history,
                cache_key="tvl-history",
            )

        else:
            self.send_error_json(404, "Not found")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"DeFi Dashboard running → http://0.0.0.0:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
