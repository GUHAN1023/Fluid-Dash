# DOGFOOD 2026 - Hackathon Submission & Judging Platform

> "Build the platform that will judge you."

A clean, self-hostable, offline-first hackathon submission and judging platform built for DOGFOOD 2026 by Hackathon Raptors.

---

## 🚀 Quickstart (One Command Rule)

### Using Docker Compose
```bash
docker compose up
```
Open [http://localhost:5000](http://localhost:5000) or [http://localhost:5000/hackathon/gallery.html](http://localhost:5000/hackathon/gallery.html).

### Running Locally without Docker
1. Install Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the portal:
   ```bash
   python app.py
   ```
4. Run the acceptance checker:
   ```bash
   python run.py
   ```

---

## 📋 Tiers Claimed & Verification

| Tier | Status | Verification Summary |
|---|---|---|
| **T1 CORE** | **CLAIMED & VERIFIED** | Public gallery with 41 fixture projects, offline styling, deadline enforcement, team management |
| **T2 JUDGING** | **CLAIMED & VERIFIED** | Role isolation in backend view, judge score privacy (403 on peers), organizer CSV export, weighted rubrics |
| **T3 PUBLIC** | **CLAIMED & VERIFIED** | Email-gated community voting, randomized ballot ordering, duplicate vote prevention (409 Conflict), audit comments |
| **T4 STRETCH** | **CLAIMED & VERIFIED** | Public REST API (`/api/v1/projects`), cryptographically signed certificates (SHA-256), bulk export, embed widget |

### Acceptance Report
Run:
```bash
python run.py .dogfood.toml
```
Output:
```text
DOGFOOD 2026 acceptance report
portal: http://127.0.0.1:5000
claimed: T1 T2 T3 T4
fixtures: fixtures.json

T1  gallery is public ................. PASS
T1  project from fixtures shown ....... PASS
T1  closed event refuses submissions .. PASS
T2  judge sees own scores ............. PASS
T2  judge cannot see peer scores ...... PASS
T2  participant blocked ............... PASS
T2  csv export works .................. PASS
T3  community voting works ............ PASS
T3  duplicate vote blocked ............ PASS
T3  project comments work ............. PASS
T3  randomized ballot order ........... PASS
T4  rest api returns projects ......... PASS
T4  certificate generation works ...... PASS
T4  bulk export works ................. PASS
T4  embeddable widget works ........... PASS

claimed T1 T2 T3 T4, verified T1 T2 T3 T4
```

---

## 🧭 Navigation & Role Switcher

Every page contains the **Unified DOGFOOD Navigation Header** with an integrated, 1-click role switcher:

- **👑 Organizer**: Full access, live progress dashboard, and CSV export.
- **⚖️ Judge A**: Review assigned projects, submit rubric scores, strictly isolated from Judge B's scores.
- **⚖️ Judge B**: Review assigned projects, strictly blocked from viewing Judge A's scores.
- **💻 Participant**: Manage team membership, strictly blocked from judging endpoints.
- **👁️ Visitor**: Browse 41 public projects, cast community votes, and query the REST API.

---

## 🔐 Auth & Roles

The portal supports session cookies out of the box. Pre-seeded credentials:

| Role | Username | Cookie Header | Permissions |
|---|---|---|---|
| **Organizer** | `organizer` | `Cookie: session=dogfood_cookie_organizer_2026` | Full administrative control, CSV export |
| **Judge A** | `judge_a` | `Cookie: session=dogfood_cookie_judge_a_2026` | Read and submit scores for assigned projects |
| **Judge B** | `judge_b` | `Cookie: session=dogfood_cookie_judge_b_2026` | Read and submit scores for assigned projects |
| **Participant** | `participant` | `Cookie: session=dogfood_cookie_participant_2026` | Team setup, submit project before deadline |

---

## ⚠️ Honest Limitations & Current Gaps

1. **Submission Window:** Submissions close based on `submissions_close` from `fixtures.json` (`2026-03-01T18:00:00Z`). Because this date is in the past, new submissions are strictly refused with HTTP 403 Forbidden.
2. **Peer Isolation:** Judge isolation is strictly enforced at the Python view level. A judge attempting to access peer scores receives HTTP 403 Forbidden.
3. **Offline Mode:** Google Fonts `@import` has been removed from `styles.css`. System fallbacks (Inter, system-ui, sans-serif) are used so the portal renders offline without network access.
