# DeFi Dashboard

Real-time DeFi analytics in the browser. Protocol TVL rankings, chain comparisons, yield pools, and interactive charts, all pulled live from the DefiLlama API.

**Stack:** `HTML · CSS · Vanilla JavaScript · Canvas API · Python 3 · DefiLlama API`

---

## Why I built this

DeFiLlama has great data but you need to jump between pages to compare protocols, chains, and yields. I wanted everything in one view with no framework overhead. The frontend is a single HTML file; the backend is a dependency-free Python proxy with a 5-minute cache so the API never gets hammered.

## Features

- **Protocol Rankings** Top 20 DeFi protocols by TVL with sparkline charts, 24h change, and category badges
- **Chain TVL Table** All chains ranked by total value locked with visual distribution bars
- **Yield Explorer** Top 100 yield pools with sortable APY, base/reward breakdown, and stablecoin filters
- **Protocol Detail Modal** Intive TVL history chart with time range selection (30D / 90D / 1Y / ALL) and hover tooltips
- **Search** Filter protocols by name in real time
- **Dark / Light Theme** System preference detection with localStorage persistence

## Setup

No dependencies. Just Python 3.
```bash
git clone https://github.com/Bitcoineo/defiDashboard.git
cd defiDashboard

# Start the server
python3 server.py

# Open in browser
open http://localhost:8000
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/protocols` | Top 20 protocols by TVL |
| `GET /api/protocol/:slug` | Protocol detail (passthrough to DefiLlama) |
| `GET /api/chains` | All chains ranked by TVL |
| `GET /api/yields` | Top 100 yield pools |
| `GET /api/sparklines` | 7-day TVL sparkline data for top protocols |
| `GET /api/tvl-history` | 30-day total DeFi TVL history |

## Architecture

The frontend is a single `index.html` file with Canvas API charts and glassmorphism styling. The backend is `server.py`, a Python stdlib HTTP server that proxies DefiLlama with a 5-minute in-memory cache. Zero external packages on either side.

## GitHub Topics

`defi` `dashboard` `defillama` `tvl` `yield-farming` `python` `vanilla-js` `crypto` `analytics`
