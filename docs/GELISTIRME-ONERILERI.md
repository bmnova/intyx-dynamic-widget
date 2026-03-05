# Development Recommendations

This document analyzes the current state of the Intyx Dynamic Widget system and lists identified improvement areas in order of priority.

---

## Current Status Summary

| Area | Status |
|------|--------|
| Backend (Python/Flask) | Production-ready, 61 tests |
| Flutter SDK | Production-ready, 16 widget types |
| Web Dashboard (React) | Working, no TypeScript |
| MCP Server | 24 tools, Gemini integration |
| CI/CD | GitHub Actions pipeline available |
| Tests (web) | **None** |
| Monitoring | **None** |

---

## High Priority

### 1. Add Web Tests

**Why:** Zero tests for the web frontend. High regression risk on code changes.

**Action items:**
- Set up Vitest + React Testing Library
- Unit tests for `WidgetStudio.jsx`, `AgentTasks.jsx`, `Dashboard.jsx`
- Basic page render tests (`Landing`, `Pricing`)
- Mock setup for API calls

**Estimated scope:** At least 20-30 tests

---

### 2. TypeScript Migration (Web)

**Why:** Web frontend is entirely `.jsx`. TypeScript is essential for catching type errors during development.

**Action items:**
- Add `tsconfig.json`, update `vite.config.js`
- `.jsx` -> `.tsx` conversion (pages + components)
- Shared `types/` folder for API response types
- Type definitions for Paddle and config files

**Recommendation:** Migrate components one at a time, don't try to do it all at once.

---

### 3. Analytics Dashboard

**Why:** Widget view, click, and dismiss data is being collected (in Firestore `user_states`) but not visualized.

**Action items:**
- Add a new "Analytics" page to the web dashboard
- Views / clicks / dismisses per widget
- Most / least interacted widgets
- Time-based charts (daily / weekly)
- Visualization with Recharts or Chart.js

---

## Medium Priority

### 4. Redis / Valkey Cache

**Why:** Currently using Firestore cache-first pattern. Under load, Firestore read costs and latency increase.

**Action items:**
- Add `redis-py` dependency
- Cache weather, news, horoscope, trend data in Redis (TTL: 15-60 min)
- Use Firestore as fallback on Redis miss
- Add `REDIS_URL` env variable (Railway / Upstash free tier)

---

### 5. JWT-Based Authentication

**Why:** Current system uses API key + License key dual system. JWT enables user-based sessions and finer permission control.

**Action items:**
- Add `PyJWT` dependency
- `/api/auth/login` and `/api/auth/refresh` endpoints
- Short-lived access token (15 min) + long-lived refresh token
- Phased removal of current API key system (for backward compatibility)

---

### 6. A/B Testing Framework

**Why:** Unknown which widget performs better for which user group.

**Action items:**
- Add `experiments` Firestore collection
- Add `experiment_id` and `variant` fields to widgets
- `/api/experiments` endpoints (create, view results)
- Experiment participation and result reporting in Flutter SDK

---

### 7. User Segmentation

**Why:** All users see the same widgets. Segment-specific widgets yield much higher conversion.

**Action items:**
- Add `target_segments` field to widget definition
- Segment criteria: platform, language, app version, custom tags
- Send segment metadata from Flutter SDK
- Add segment filter to trigger engine

---

### 8. Widget Scheduling

**Why:** Widgets that need to be shown at specific times or date ranges cannot be managed with the current trigger system.

**Action items:**
- Add `show_from`, `show_until`, `show_hours` (e.g. 08:00-20:00) fields to widgets
- Add time-based condition to trigger engine
- Calendar view scheduling in the web dashboard

---

### 9. Streaming AI Response

**Why:** Gemini content generation can take long; the user waits for the result.

**Action items:**
- Add SSE (Server-Sent Events) support to `/api/ai/generate-content` endpoint
- Show stream in real-time on web dashboard
- Handle stream response in Flutter SDK

---

## Low Priority

### 10. React Native SDK

**Why:** Flutter SDK exists but the React Native market is also large.

**Action items:**
- Create `react-native-intyx-widget` package
- JSON-driven rendering using the same REST API
- Publish to npm

---

### 11. Kubernetes Manifests

**Why:** Currently only Dockerfile and Railway/Render config exist. Enterprise customers expect k8s.

**Action items:**
- Create `k8s/` directory
- Deployment, Service, Ingress, ConfigMap, Secret manifests
- Horizontal Pod Autoscaler (HPA) config
- Helm chart (optional)

---

### 12. Monitoring & Observability

**Why:** No visibility into what's happening in production (Sentry is optionally added but not sufficient).

**Action items:**
- Add Prometheus metrics endpoint (`/metrics`): request count, latency, error rate
- Prepare Grafana dashboard template
- Structured logging (JSON format, log level)
- Uptime monitoring (Better Uptime / UptimeRobot)

---

### 13. Usage Report Email

**Why:** Customers want to see how many widgets were displayed monthly.

**Action items:**
- Monthly usage summary email (Resend / SendGrid)
- `/api/usage/report` endpoint
- License plan usage percentage display

---

### 14. API Versioning

**Why:** Existing clients can break on API changes. No versioning strategy.

**Action items:**
- URL prefix: `/api/v1/` -> `/api/v2/`
- Deprecation headers
- Version migration guide document

---

### 15. Dark Mode (Web Dashboard)

**Why:** No dark mode in web dashboard. Developer target audience expects dark mode.

**Action items:**
- Tailwind `dark:` classes or CSS variables
- Auto-detect system preference (`prefers-color-scheme`)
- Manual toggle (in Navbar)

---

### 16. i18n / Multi-Language Support

**Why:** Project has Turkish docs but widget content is in English. i18n is essential for going global.

**Action items:**
- Web dashboard translation with `react-i18next`
- `locale` parameter in widget content
- Fetch content by `locale` in Flutter SDK
- Initial TR and EN translations

---

## Priority Summary

| # | Improvement | Priority | Impact | Difficulty |
|---|---|---|---|---|
| 1 | Add web tests | High | Code reliability | Low |
| 2 | TypeScript migration | High | Maintainability | Medium |
| 3 | Analytics dashboard | High | User value | Medium |
| 4 | Redis cache | Medium | Performance | Low |
| 5 | JWT auth | Medium | Security | Medium |
| 6 | A/B testing | Medium | Business value | High |
| 7 | User segmentation | Medium | Business value | Medium |
| 8 | Widget scheduling | Medium | Feature | Low |
| 9 | Streaming AI | Medium | UX | Medium |
| 10 | React Native SDK | Low | Market | High |
| 11 | Kubernetes | Low | Infrastructure | High |
| 12 | Monitoring | Low | Operations | Medium |
| 13 | Usage report | Low | Customer value | Low |
| 14 | API versioning | Low | Maintenance | Low |
| 15 | Dark mode | Low | UX | Low |
| 16 | i18n | Low | Global market | Medium |
