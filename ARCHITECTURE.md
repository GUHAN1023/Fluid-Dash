# Architecture & System Design

## 1. Overview
The platform is designed around strict backend enforcement, offline operability, and zero external cloud dependencies.

```
                  +---------------------------+
                  | Browser / Acceptance Test |
                  +-------------+-------------+
                                |
                   HTTP Cookie / Headers
                                |
                  +-------------v-------------+
                  |       Flask Backend       |
                  |          app.py           |
                  +------+-------------+------+
                         |             |
        Jinja2 Templates |             | SQL Queries
                         v             v
                  +------------+ +------------+
                  | templates/ | | dogfood.db |
                  |  static/   | |  (SQLite)  |
                  +------------+ +------------+
```

## 2. Core Architectural Decisions

### A. Backend-Enforced Role Isolation
Unlike platforms that merely hide unauthorized UI buttons in the client, role permissions are checked in Python view functions prior to data access:
- If a user lacks a session cookie, protected endpoints return `401 Unauthorized`.
- If a participant attempts to access `/judge/scores/...`, the route returns `403 Forbidden`.
- If a judge attempts to access another judge's score sheet (`/judge/scores/<peer_id>`), the route returns `403 Forbidden`.
- If a non-organizer accesses `/export/csv`, the route returns `403 Forbidden`.

### B. Offline & Self-Hostable
All asset dependencies (fonts, styles, scripts) are hosted locally. Remote Google Fonts `@import` was removed to ensure full operability on air-gapped laptops.

### C. Server-Side Templated Gallery
To guarantee that search engines, acceptance tests, and low-powered clients see all submitted projects immediately on load without JavaScript hydration delays, `gallery.html` renders all fixture projects directly via Jinja2 iteration blocks.
