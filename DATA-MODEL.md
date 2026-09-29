# Data Model & Schema

## SQLite Tables

### 1. `events`
Stores hackathon metadata and lifecycle deadlines.
- `id` (TEXT, PK): E.g. `evt_01`
- `name` (TEXT): E.g. `Sample Hack 2026`
- `submissions_close` (TEXT): ISO 8601 UTC timestamp

### 2. `tracks`
Hackathon focus areas and challenges.
- `id` (TEXT, PK): E.g. `trk_01`
- `name` (TEXT): E.g. `Developer tools`

### 3. `judges`
Invited evaluation panel members.
- `id` (TEXT, PK): E.g. `jdg_01`
- `name` (TEXT): Judge's full name
- `email` (TEXT): Contact email
- `tracks` (TEXT): JSON array of assigned track IDs

### 4. `teams`
Participant teams.
- `id` (TEXT, PK): E.g. `tm_01`
- `name` (TEXT): Team name
- `members` (TEXT): JSON array of member emails

### 5. `projects`
Submitted hackathon submissions.
- `id` (TEXT, PK): E.g. `prj_01`
- `team` (TEXT, FK -> teams.id)
- `track` (TEXT, FK -> tracks.id)
- `title` (TEXT): Submission title
- `summary` (TEXT): 1-sentence elevator pitch
- `repo_url` (TEXT): Public code repository
- `submitted_at` (TEXT): ISO 8601 UTC timestamp

### 6. `scores`
Evaluations submitted by judges.
- `id` (INTEGER, PK AUTOINCREMENT)
- `judge` (TEXT, FK -> judges.id)
- `project` (TEXT, FK -> projects.id)
- `functionality` (INTEGER): Score 1-5
- `quality` (INTEGER): Score 1-5
- `innovation` (INTEGER): Score 1-5
- `comment` (TEXT): Qualitative notes

### 7. `users`
Authenticated portal identities.
- `id` (TEXT, PK)
- `username` (TEXT, UNIQUE)
- `role` (TEXT): `organizer`, `judge`, `participant`
- `judge_id` (TEXT, Nullable): Foreign link to judges table
- `cookie_token` (TEXT, UNIQUE): Session cookie identifier
