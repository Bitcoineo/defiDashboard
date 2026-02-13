# DeFi Dashboard — Build Progress

## Backend (server.py)
- [x] HTTP server with ThreadingHTTPServer on port 8000
- [x] Static file serving for index.html
- [x] `/api/protocols` — top 20 by TVL from DeFiLlama
- [x] `/api/protocol/<slug>` — protocol detail passthrough
- [x] `/api/chains` — chain TVL rankings sorted desc
- [x] `/api/yields` — filtered top 100 pools (tvlUsd > 10K, apy < 1000, no outliers)
- [x] `/api/sparklines` — 7-day TVL history for top protocols (parallel fetch)
- [x] 5-minute in-memory cache for all endpoints
- [x] SSL fix for macOS (certifi CA bundle)
- [x] CORS headers on all responses
- [x] CEX protocols filtered out from `/api/protocols`

## Frontend (index.html)
- [x] Glassmorphism redesign (light gradient bg, frosted glass cards, Inter font)
- [x] Indigo accent color (#6366f1), no terminal/hacker aesthetic
- [x] Dark theme with toggle button (sun/moon, top-right)
- [x] Theme persisted in localStorage, auto-detects system preference
- [x] Flash-of-wrong-theme prevention (inline script in `<head>`)
- [x] Smooth theme transition (0.3s on bg, color, border, shadow)
- [x] SVG logo icon (stacked layers) as home button
- [x] Logo click: returns to Protocols tab, closes modal, clears search
- [x] Tab navigation: pill-shaped Protocols | Chains | Yields
- [x] Protocols tab: glass card grid with logo, name, TVL, 24h change, category, chain count
- [x] Chains tab: ranked table with TVL distribution bars
- [x] Yields tab: sortable table with APY color-coding, stablecoin badges
- [x] Search bar filtering protocols by name
- [x] Sparkline charts on protocol cards (theme-aware colors)
- [x] Protocol detail modal — fully opaque background (100% opacity)
- [x] Canvas TVL history chart (theme-aware colors, hover crosshair)
- [x] Time range buttons on chart (ALL / 1Y / 90D / 30D)
- [x] Charts + sparklines redraw on theme toggle
- [x] Loading skeletons (theme-aware shimmer)
- [x] Lazy tab loading (fetch data only on first visit)
- [x] Image fallback for broken protocol logos
- [x] Responsive design (3/2/1 columns, header wraps on mobile)
- [x] Keyboard support (Escape to close modal)

## Testing
- [x] All 5 API endpoints return correct data
- [x] CEX protocols excluded (0 CEX in results)
- [x] 23/23 feature checks passed (dark theme, toggle, logo, modal opacity, etc.)
- [ ] Visual verification in browser
