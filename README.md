# DOGFOOD 2026 - Hackathon Submission & Judging Platform

> "Build the platform that will judge you."

A clean, self-hostable, offline-first hackathon submission and judging platform built for DOGFOOD 2026.

---

## 🚀 Quickstart (One Command)

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

| Tier | Status | Verification |
|---|---|---|
| **T1 CORE** | **CLAIMED & VERIFIED** | Public gallery with 41 fixture projects, offline styling, deadline enforcement, team management |
| **T2 JUDGING** | **CLAIMED & VERIFIED** | Role isolation in backend view, judge score privacy, organizer CSV export, weighted rubrics |

### Acceptance Report
Run:
```bash
python run.py .dogfood.toml
```
Output:
```text
DOGFOOD 2026 acceptance report
portal: http://127.0.0.1:5000
claimed: T1 T2
fixtures: fixtures.json

T1  gallery is public ................. PASS
T1  project from fixtures shown ....... PASS
T1  closed event refuses submissions .. PASS
T2  judge sees own scores ............. PASS
T2  judge cannot see peer scores ...... PASS
T2  participant blocked ............... PASS
T2  csv export works .................. PASS

claimed T1 T2, verified T1 T2
```

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
