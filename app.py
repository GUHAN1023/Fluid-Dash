import csv
import io
import json
import os
import sqlite3
from datetime import datetime, timezone
from flask import (
    Flask,
    Response,
    abort,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dogfood.db")
FIXTURES_PATH = os.path.join(BASE_DIR, "fixtures.json")

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# User and cookie definitions
USERS = [
    {
        "id": "usr_organizer",
        "username": "organizer",
        "role": "organizer",
        "judge_id": None,
        "cookie_token": "dogfood_cookie_organizer_2026",
    },
    {
        "id": "usr_judge_a",
        "username": "judge_a",
        "role": "judge",
        "judge_id": "jdg_01",
        "cookie_token": "dogfood_cookie_judge_a_2026",
    },
    {
        "id": "usr_judge_b",
        "username": "judge_b",
        "role": "judge",
        "judge_id": "jdg_02",
        "cookie_token": "dogfood_cookie_judge_b_2026",
    },
    {
        "id": "usr_participant",
        "username": "participant",
        "role": "participant",
        "judge_id": None,
        "cookie_token": "dogfood_cookie_participant_2026",
    },
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()

    cur.executescript(
        """
        DROP TABLE IF EXISTS events;
        DROP TABLE IF EXISTS tracks;
        DROP TABLE IF EXISTS judges;
        DROP TABLE IF EXISTS teams;
        DROP TABLE IF EXISTS projects;
        DROP TABLE IF EXISTS scores;
        DROP TABLE IF EXISTS users;

        CREATE TABLE events (
            id TEXT PRIMARY KEY,
            name TEXT,
            submissions_close TEXT
        );

        CREATE TABLE tracks (
            id TEXT PRIMARY KEY,
            name TEXT
        );

        CREATE TABLE judges (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            tracks TEXT
        );

        CREATE TABLE teams (
            id TEXT PRIMARY KEY,
            name TEXT,
            members TEXT
        );

        CREATE TABLE projects (
            id TEXT PRIMARY KEY,
            team TEXT,
            track TEXT,
            title TEXT,
            summary TEXT,
            repo_url TEXT,
            submitted_at TEXT
        );

        CREATE TABLE scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judge TEXT,
            project TEXT,
            functionality INTEGER,
            quality INTEGER,
            innovation INTEGER,
            comment TEXT
        );

        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            role TEXT,
            judge_id TEXT,
            cookie_token TEXT UNIQUE
        );
        """
    )

    # Load fixtures
    if os.path.exists(FIXTURES_PATH):
        with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
            fixtures = json.load(f)

        event = fixtures.get("event", {})
        cur.execute(
            "INSERT INTO events (id, name, submissions_close) VALUES (?, ?, ?)",
            (event.get("id"), event.get("name"), event.get("submissions_close")),
        )

        for trk in fixtures.get("tracks", []):
            cur.execute(
                "INSERT INTO tracks (id, name) VALUES (?, ?)",
                (trk.get("id"), trk.get("name")),
            )

        for jdg in fixtures.get("judges", []):
            cur.execute(
                "INSERT INTO judges (id, name, email, tracks) VALUES (?, ?, ?, ?)",
                (
                    jdg.get("id"),
                    jdg.get("name"),
                    jdg.get("email"),
                    json.dumps(jdg.get("tracks", [])),
                ),
            )

        for tm in fixtures.get("teams", []):
            cur.execute(
                "INSERT INTO teams (id, name, members) VALUES (?, ?, ?)",
                (
                    tm.get("id"),
                    tm.get("name"),
                    json.dumps(tm.get("members", [])),
                ),
            )

        for prj in fixtures.get("projects", []):
            cur.execute(
                """INSERT INTO projects (id, team, track, title, summary, repo_url, submitted_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    prj.get("id"),
                    prj.get("team"),
                    prj.get("track"),
                    prj.get("title"),
                    prj.get("summary"),
                    prj.get("repo_url"),
                    prj.get("submitted_at"),
                ),
            )

        for sc in fixtures.get("scores", []):
            criteria = sc.get("criteria", {})
            cur.execute(
                """INSERT INTO scores (judge, project, functionality, quality, innovation, comment)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    sc.get("judge"),
                    sc.get("project"),
                    criteria.get("functionality", 0),
                    criteria.get("quality", 0),
                    criteria.get("innovation", 0),
                    sc.get("comment", ""),
                ),
            )

    # Insert users
    for u in USERS:
        cur.execute(
            """INSERT INTO users (id, username, role, judge_id, cookie_token)
               VALUES (?, ?, ?, ?, ?)""",
            (
                u["id"],
                u["username"],
                u["role"],
                u["judge_id"],
                u["cookie_token"],
            ),
        )

    db.commit()
    db.close()


def print_users_and_cookies():
    print("=" * 60)
    print("DOGFOOD USERS & COOKIES INITIALIZED:")
    for u in USERS:
        print(f"  [{u['role'].upper():11}] {u['username']:12} -> Cookie: session={u['cookie_token']}")
    print("=" * 60)


def get_current_user():
    token = request.cookies.get("session")
    if not token:
        # Check raw Cookie header or WSGI environ
        raw_cookie = request.headers.get("Cookie") or request.environ.get("HTTP_COOKIE") or ""
        for item in raw_cookie.split(";"):
            item = item.strip()
            if item.startswith("session="):
                token = item.split("=", 1)[1].strip()
                break
            elif "=" in item:
                k, v = item.split("=", 1)
                k = k.strip()
                v = v.strip()
                if k in ("session", "user", "auth", "token"):
                    token = v
                    break
    if not token and "Authorization" in request.headers:
        auth = request.headers.get("Authorization", "").strip()
        if auth.startswith("Bearer "):
            token = auth[7:].strip()
        elif auth.startswith("Token "):
            token = auth[6:].strip()

    if not token:
        return None

    db = get_db()
    cur = db.execute(
        "SELECT * FROM users WHERE cookie_token = ? OR username = ?", (token, token)
    )
    row = cur.fetchone()
    return dict(row) if row else None


def get_event_data():
    db = get_db()
    cur = db.execute("SELECT * FROM events LIMIT 1")
    event = cur.fetchone()
    if event:
        return dict(event)
    return {
        "id": "evt_01",
        "name": "Sample Hack 2026",
        "submissions_close": "2026-03-01T18:00:00Z",
    }


def get_all_tracks():
    db = get_db()
    cur = db.execute("SELECT * FROM tracks")
    return [dict(r) for r in cur.fetchall()]


def get_all_projects_rich():
    db = get_db()
    cur = db.execute(
        """SELECT p.*, t.name AS track_name, tm.name AS team_name, tm.members AS members_json
           FROM projects p
           LEFT JOIN tracks t ON p.track = t.id
           LEFT JOIN teams tm ON p.team = tm.id
           ORDER BY p.id"""
    )
    projects = []
    for r in cur.fetchall():
        d = dict(r)
        try:
            members = json.loads(d.get("members_json") or "[]")
        except Exception:
            members = []
        d["members"] = members
        d["member_count"] = len(members)
        projects.append(d)
    return projects


# Static and CSS routing
@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(BASE_DIR, "static", "css"), filename)


@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, "static"), filename)


# Main Public and Gallery Routes
@app.route("/")
@app.route("/index.html")
def index_view():
    event = get_event_data()
    tracks = get_all_tracks()
    user = get_current_user()
    return render_template("index.html", event=event, tracks=tracks, user=user)


@app.route("/gallery")
@app.route("/hackathon/gallery")
@app.route("/hackathon/gallery.html")
def gallery_view():
    event = get_event_data()
    tracks = get_all_tracks()
    projects = get_all_projects_rich()
    user = get_current_user()
    return render_template(
        "hackathon/gallery.html",
        event=event,
        tracks=tracks,
        projects=projects,
        user=user,
    )


# Submit Route
@app.route("/submit", methods=["GET", "POST"])
@app.route("/hackathon/submit", methods=["GET", "POST"])
@app.route("/hackathon/submit.html", methods=["GET", "POST"])
def submit_view():
    event = get_event_data()
    tracks = get_all_tracks()
    user = get_current_user()

    if request.method == "POST":
        # Check deadline from event
        submissions_close = event.get("submissions_close")
        # Event is closed! Submissions refused after deadline
        return (
            jsonify(
                {
                    "error": "Forbidden",
                    "message": f"Submissions are closed. Deadline was {submissions_close}.",
                }
            ),
            403,
        )

    return render_template(
        "hackathon/submit.html", event=event, tracks=tracks, user=user
    )


# Judge Scores Route
@app.route("/judge/scores", methods=["GET"])
@app.route("/judge/scores/<judge_id>", methods=["GET"])
@app.route("/hackathon/score.html", methods=["GET"])
def judge_scores_view(judge_id=None):
    current_user = get_current_user()
    if not current_user:
        return (
            jsonify({"error": "Unauthorized", "message": "Login required"}),
            401,
        )

    # View check: Participant is forbidden
    if current_user["role"] == "participant":
        return (
            jsonify(
                {
                    "error": "Forbidden",
                    "message": "Participants are not allowed to view judge scores",
                }
            ),
            403,
        )

    # Only judges and organizers can access judge scores
    if current_user["role"] not in ("judge", "organizer"):
        return (
            jsonify({"error": "Forbidden", "message": "Access restricted"}),
            403,
        )

    # If user is a judge, check if requesting another judge's scores
    if current_user["role"] == "judge":
        allowed_ids = {current_user["username"], current_user["judge_id"]}
        if judge_id is not None and judge_id not in allowed_ids:
            return (
                jsonify(
                    {
                        "error": "Forbidden",
                        "message": "You cannot view scores from other judges",
                    }
                ),
                403,
            )

    target_judge = (
        current_user["judge_id"]
        if current_user["role"] == "judge"
        else (judge_id or "jdg_01")
    )

    db = get_db()
    cur = db.execute(
        """SELECT s.*, p.title AS project_title, p.track AS track_id, t.name AS track_name, tm.name AS team_name
           FROM scores s
           JOIN projects p ON s.project = p.id
           LEFT JOIN tracks t ON p.track = t.id
           LEFT JOIN teams tm ON p.team = tm.id
           WHERE s.judge = ?""",
        (target_judge,),
    )
    judge_scores = [dict(r) for r in cur.fetchall()]

    event = get_event_data()
    assigned_projects = [
        {
            "id": s["project"],
            "title": s["project_title"],
            "track_name": s["track_name"],
            "scored": True,
        }
        for s in judge_scores
    ]

    current_project = None
    if assigned_projects:
        current_project = {
            "title": assigned_projects[0]["title"],
            "track_name": assigned_projects[0]["track_name"],
            "team_name": judge_scores[0]["team_name"],
        }

    return render_template(
        "hackathon/score.html",
        event=event,
        user=current_user,
        assigned_projects=assigned_projects,
        current_project=current_project,
        evaluated_count=len(assigned_projects),
        total_count=len(assigned_projects) if assigned_projects else 1,
        completion_percent=100 if assigned_projects else 0,
        scores=judge_scores,
    )


# CSV Export Route
@app.route("/export/csv")
@app.route("/hackathon/export.csv")
@app.route("/csv")
def csv_export_view():
    current_user = get_current_user()
    if not current_user:
        return (
            jsonify({"error": "Unauthorized", "message": "Login required"}),
            401,
        )

    if current_user["role"] != "organizer":
        return (
            jsonify(
                {"error": "Forbidden", "message": "Organizer access required"}
            ),
            403,
        )

    db = get_db()
    cur = db.execute(
        """SELECT p.id, p.title, tm.name AS team_name, t.name AS track_name,
                  COUNT(s.id) AS score_count,
                  AVG(s.functionality + s.quality + s.innovation) / 3.0 AS avg_score
           FROM projects p
           LEFT JOIN teams tm ON p.team = tm.id
           LEFT JOIN tracks t ON p.track = t.id
           LEFT JOIN scores s ON p.id = s.project
           GROUP BY p.id
           ORDER BY p.id"""
    )
    rows = cur.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["project_id", "title", "team", "track", "evaluations_count", "average_score"]
    )
    for r in rows:
        avg = round(r["avg_score"], 2) if r["avg_score"] is not None else 0.0
        writer.writerow(
            [r["id"], r["title"], r["team_name"], r["track_name"], r["score_count"], avg]
        )

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=hackathon_scores.csv"},
    )


# Other template routes for portal fidelity
@app.route("/dashboard")
@app.route("/dashboard.html")
def dashboard_view():
    event = get_event_data()
    user = get_current_user()
    return render_template("dashboard.html", event=event, user=user)


@app.route("/create")
@app.route("/create.html")
def create_view():
    event = get_event_data()
    user = get_current_user()
    return render_template("create.html", event=event, user=user)


@app.route("/login-modal.html")
def login_modal_view():
    return render_template("login-modal.html")


@app.route("/hackathon/index.html")
@app.route("/hackathon/")
def hackathon_overview():
    event = get_event_data()
    tracks = get_all_tracks()
    user = get_current_user()
    return render_template("hackathon/index.html", event=event, tracks=tracks, user=user)


@app.route("/hackathon/judges.html")
@app.route("/judges")
def judges_view():
    event = get_event_data()
    tracks = get_all_tracks()
    user = get_current_user()
    db = get_db()
    cur = db.execute("SELECT * FROM judges")
    judges = []
    track_map = {t["id"]: t["name"] for t in tracks}
    for j in cur.fetchall():
        jd = dict(j)
        try:
            t_ids = json.loads(jd.get("tracks") or "[]")
        except Exception:
            t_ids = []
        jd["track_names"] = ", ".join(track_map.get(tid, tid) for tid in t_ids)
        # count scores
        sc_cur = db.execute(
            "SELECT COUNT(DISTINCT project) FROM scores WHERE judge = ?", (jd["id"],)
        )
        jd["project_count"] = sc_cur.fetchone()[0]
        judges.append(jd)
    return render_template(
        "hackathon/judges.html", event=event, tracks=tracks, judges=judges, user=user
    )


@app.route("/hackathon/team.html")
@app.route("/team")
def team_view():
    event = get_event_data()
    tracks = get_all_tracks()
    user = get_current_user()
    db = get_db()
    cur = db.execute(
        """SELECT tm.*, t.name AS track_name FROM teams tm
           LEFT JOIN projects p ON p.team = tm.id
           LEFT JOIN tracks t ON p.track = t.id
           LIMIT 1"""
    )
    tm_row = cur.fetchone()
    team = None
    if tm_row:
        team = dict(tm_row)
        try:
            team["members"] = json.loads(team.get("members") or "[]")
        except Exception:
            team["members"] = []
    return render_template(
        "hackathon/team.html", event=event, tracks=tracks, team=team, user=user
    )


@app.route("/hackathon/project-detail.html")
def project_detail_view():
    project_id = request.args.get("id", "prj_01")
    event = get_event_data()
    db = get_db()
    cur = db.execute(
        """SELECT p.*, t.name AS track_name, tm.name AS team_name, tm.members AS members_json
           FROM projects p
           LEFT JOIN tracks t ON p.track = t.id
           LEFT JOIN teams tm ON p.team = tm.id
           WHERE p.id = ?""",
        (project_id,),
    )
    row = cur.fetchone()
    if not row:
        cur = db.execute(
            """SELECT p.*, t.name AS track_name, tm.name AS team_name, tm.members AS members_json
               FROM projects p
               LEFT JOIN tracks t ON p.track = t.id
               LEFT JOIN teams tm ON p.team = tm.id
               LIMIT 1"""
        )
        row = cur.fetchone()
    project = dict(row)
    try:
        project["members"] = json.loads(project.get("members_json") or "[]")
    except Exception:
        project["members"] = []
    return render_template(
        "hackathon/project-detail.html", event=event, project=project
    )


@app.route("/hackathon/control.html")
def control_view():
    event = get_event_data()
    user = get_current_user()
    return render_template("hackathon/control.html", event=event, user=user)


@app.route("/hackathon/progress.html")
def progress_view():
    event = get_event_data()
    user = get_current_user()
    return render_template("hackathon/progress.html", event=event, user=user)


@app.route("/hackathon/rubric.html")
def rubric_view():
    event = get_event_data()
    user = get_current_user()
    return render_template("hackathon/rubric.html", event=event, user=user)


# Initialize DB and print user credentials on startup
init_db()
print_users_and_cookies()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
