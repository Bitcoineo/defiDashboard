# DeFi Dashboard

A real-time DeFi analytics dashboard powered by the [DefiLlama API](https://defillama.com/docs/api). Track protocol TVL, chain rankings, and yield opportunities in a single-page glassmorphism UI.

## Features

- **Protocol Rankings** — Top 20 DeFi protocols by TVL with sparkline charts, 24h change, and category badges
- **Chain TVL Table** — All chains ranked by total value locked with visual distribution bars
- **Yield Explorer** — Top 100 yield pools with sortable APY, base/reward breakdown, and stablecoin filters
- **Protocol Detail Modal** — Interactive TVL history chart with time range selection (30D/90D/1Y/ALL) and hover tooltips
- **Dark/Light Theme** — Toggleable with system preference detection and localStorage persistence
- **Search** — Filter protocols by name in real-time

## Tech Stack

- **Frontend:** Single `index.html` file — vanilla HTML/CSS/JS, Canvas API for charts, glassmorphism design with Inter font
- **Backend:** `server.py` — Python stdlib HTTP server (no dependencies), proxies DefiLlama API with 5-minute in-memory cache

## Getting Started

```bash
# macOS
python3 server.py

# Linux / Windows
python server.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/protocols` | Top 20 protocols by TVL |
| `GET /api/protocol/:slug` | Protocol detail (passthrough to DefiLlama) |
| `GET /api/chains` | All chains ranked by TVL |
| `GET /api/yields` | Top 100 yield pools (filtered) |
| `GET /api/sparklines` | 7-day TVL sparkline data for top protocols |
| `GET /api/tvl-history` | 30-day total DeFi TVL history |
