# DermoBrain Platform — Demo Script & Cost Breakdown

## Live URLs

| Resource | URL |
|----------|-----|
| Main Site | https://www.dermobrain.com |
| Practice Portal | https://www.dermobrain.com/practice/portal.html |
| API Health | https://dermobrain-api.naren-6e3.workers.dev/api/health |

---

## Demo Credentials

| Role | Login | Password |
|------|-------|----------|
| **Admin** | (code-based) | `admin2024` |
| **Practice Owner** | `dr.shukla@drsskincare.ca` | `drs2024` |
| **Editor** | `sarah.chen@drsskincare.ca` | `editor2024` |
| **Staff Training** | `sarah.mitchell@drsskincare.ca` | `staff2024` |

---

## Demo Walkthrough (5–7 minutes)

### 1. The Content Library (1 min)

Start at the homepage: **dermobrain.com**

- "DermoBrain is an evidence-based dermatology content platform with over 1,000 articles across 20 categories."
- Click into any category (e.g., Skin Conditions → Acne Vulgaris)
- Show the article quality: real statistics, drug names, dosages, peer-reviewed references
- Point out the SEO-optimized structure: breadcrumbs, related articles, meta descriptions

### 2. The Unified Portal (1 min)

Navigate to **dermobrain.com/practice/portal.html**

- "Every user enters through a single portal and gets routed to their role-specific dashboard."
- Show the four role cards: Admin, Editor, Practice Owner, Staff Training
- "Each card flips to a login form — clean, intuitive."

### 3. Practice Owner Dashboard (2 min)

Click **Practice Owner** → enter `dr.shukla@drsskincare.ca` / `drs2024`

- **KPI Cards**: "Dr. Shukla sees his practice's real-time metrics — 43,000+ article views, 3 active editors, average quality score of 88.5 across 20 articles."
- **Recent Edits**: "Every edit is tracked with editor name, article, date, and approval status."
- **Analytics**: "Score distribution chart shows content quality at a glance. Key metrics break down performance."
- **Navigation**: Point out sidebar sections — Content, Training, Branding, Team

Click **Logout** to return to portal.

### 4. Editor Dashboard (1.5 min)

Click **Editor Portal** → enter `sarah.chen@drsskincare.ca` / `editor2024`

- **Welcome Banner**: "Sarah sees her name, specialty, and current tier badge."
- **Stats**: "8 articles reviewed, Senior tier, 18-minute average review time."
- **Tier Progress**: "Gamified progression — 53% to Editor tier. 8 of 15 reviews completed."
- **Recent Reviews**: "Her last 5 reviews with statuses — Approved, Approved with Notes, Request Revision."
- **Available for Review**: "3 articles in her specialty waiting for review."

Click **Logout**.

### 5. Admin Dashboard (1 min)

Click **Admin Portal** → enter code `admin2024`

- **Platform Overview**: "47 editors, 12 practices, 312 articles reviewed, 8 pending applications."
- **Growth Chart**: "Monthly editor signups trending upward — 18 in January to 32 in June."
- **Activity Feed**: "Real-time feed of applications, reviews, flags, and promotions."
- **Navigation**: Editor Management, Practice Management, Content, Issues, Badges, Settings, Video Library

### 6. Technical Architecture (30 sec)

- "Backend: Cloudflare Workers + D1 database — serverless, globally distributed, sub-50ms response times."
- "Frontend: Static site on GitHub Pages with Cloudflare CDN — instant page loads."
- "API: Full REST endpoints with role-based auth, session management, and per-practice branding."
- "Zero server maintenance. Auto-scales to any traffic level."

---

## Architecture Overview

```
[Browser] → [Cloudflare CDN] → [GitHub Pages - Static Content]
                ↓
         [Cloudflare Workers API]
                ↓
         [D1 Database (SQLite at Edge)]
```

**Static Layer**: 47,000+ pages on GitHub Pages, served through Cloudflare CDN with full SSL/TLS.

**API Layer**: Cloudflare Worker handling auth, dashboards, articles, branding, and user management.

**Database**: Cloudflare D1 with 6 tables — practices, users, articles, practice_articles, article_edits, sessions — plus 12 performance indexes.

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/health` | No | Health check |
| POST | `/api/auth/login` | No | Login (returns token) |
| POST | `/api/auth/logout` | Yes | Logout (invalidates session) |
| GET | `/api/auth/me` | Yes | Current user + practice info |
| GET | `/api/articles` | Yes | List articles (paginated, filterable) |
| GET | `/api/articles/:id` | Yes | Single article detail |
| GET | `/api/dashboard/practice/:id` | Yes | Practice dashboard stats |
| GET | `/api/dashboard/editor/:id` | Yes | Editor dashboard stats |
| GET | `/api/branding/:slug` | No | Public practice branding |
| GET | `/api/branding-loader.js` | No | Dynamic CSS loader script |
| POST | `/api/setup` | No | Seed database (one-time) |

---

## Monthly Cost Breakdown

### Current Costs (Free Tier)

| Service | Free Tier | Current Usage | Monthly Cost |
|---------|-----------|---------------|--------------|
| **GitHub Pages** | Unlimited static hosting | 47K pages | **$0** |
| **Cloudflare DNS + CDN** | Free plan | Unlimited bandwidth | **$0** |
| **Cloudflare Workers** | 100K requests/day | ~1K requests/day | **$0** |
| **Cloudflare D1** | 5M reads, 100K writes/day | ~500 reads/day | **$0** |
| **Domain** | — | dermobrain.com (annual) | **~$1/mo** |
| | | **Total** | **~$1/month** |

### At Scale (10K daily users)

| Service | Tier | Estimated Cost |
|---------|------|----------------|
| **GitHub Pages** | Free (unlimited) | $0 |
| **Cloudflare CDN** | Pro plan | $20/mo |
| **Cloudflare Workers** | Paid ($5/mo + usage) | $5–15/mo |
| **Cloudflare D1** | Paid (beyond free tier) | $0.75/mo per 1M reads |
| **Domain** | Annual renewal | ~$1/mo |
| | **Total at 10K daily users** | **~$30–40/month** |

### At Enterprise Scale (100K daily users)

| Service | Estimated Cost |
|---------|----------------|
| Cloudflare Business | $200/mo |
| Workers + D1 at volume | $50–100/mo |
| **Total** | **~$250–300/month** |

### Cost Comparison

| Platform | 10K users/day | 100K users/day |
|----------|---------------|----------------|
| **DermoBrain (current)** | **$30–40/mo** | **$250–300/mo** |
| AWS (EC2 + RDS + CloudFront) | $150–300/mo | $800–1,500/mo |
| Vercel + PlanetScale | $70–150/mo | $400–800/mo |
| WordPress + Managed Hosting | $100–200/mo | $500–1,000/mo |

---

## Seeded Database Content

**2 Practices**: DRS Skincare (Toronto) and ClearView Dermatology (Vancouver)

**7 Users**: 1 admin, 2 practice owners, 4 editors across specialties

**20 Articles**: Covering Medical Derm, Cosmetic Derm, Surgical Derm, Pediatric Derm — each with quality scores, view counts, and word counts

**12 Article Edits**: Mix of approved, pending, and revision-requested edits with realistic timestamps

---

## Key Technical Decisions

1. **Cloudflare Workers over traditional servers** — Zero cold starts, global edge deployment, no infrastructure management
2. **D1 over external databases** — Co-located with Workers for sub-millisecond reads, no connection pooling needed
3. **Static-first architecture** — 99% of content is pre-built HTML; API only handles dynamic dashboard data
4. **SHA-256 password hashing with random salts** — Using Web Crypto API (native to Workers runtime)
5. **Session-based auth over JWTs** — Server-side session validation, easy revocation, no token size bloat

---

## Files & Deployment

| File | Location | Purpose |
|------|----------|---------|
| `worker.js` | Cloudflare Workers | API backend (730 lines) |
| `wrangler.toml` | Deploy config | Worker + D1 binding |
| `portal.html` | `/practice/portal.html` | Unified login portal |
| `dashboard-practice.html` | `/practice/dashboard-practice.html` | Practice owner dashboard |
| `editor-dashboard.html` | `/practice/editor-dashboard.html` | Editor dashboard |
| `editor-admin.html` | `/practice/editor-admin.html` | Admin dashboard |
| `build.py` | Root | Static site generator |
| 20 JSON files | `/data/` | Article content database |

**To redeploy the API:**
```bash
cd ~/ClaudeMacStudio/dermobrain-deploy
npx wrangler deploy
```

**To rebuild the static site:**
```bash
cd ~/ClaudeMacStudio/dermobrain
python3 build.py
```
