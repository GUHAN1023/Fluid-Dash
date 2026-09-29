import urllib.request
import urllib.error
import json
import time

base = "http://127.0.0.1:5000"

def test_url(path, headers=None, method="GET", body=None):
    req = urllib.request.Request(base + path, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if body is not None:
        req.data = json.dumps(body).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

unique_email = f"voter_{int(time.time()*1000)}@domain.com"

tests = [
    # Core & Assets
    ("CSS styles", "/css/styles.css", None, 200, "GET", None),
    ("CSS components", "/css/components.css", None, 200, "GET", None),
    ("Home / Index", "/", None, 200, "GET", None),
    ("Dashboard", "/dashboard.html", None, 200, "GET", None),
    ("Create Hackathon", "/create.html", None, 200, "GET", None),
    ("Hackathon Overview", "/hackathon/index.html", None, 200, "GET", None),
    ("Hackathon Gallery", "/hackathon/gallery.html", None, 200, "GET", None),
    ("Project Detail prj_01", "/hackathon/project-detail.html?id=prj_01", None, 200, "GET", None),
    ("Project Detail prj_41", "/hackathon/project-detail.html?id=prj_41", None, 200, "GET", None),
    ("Team Setup", "/hackathon/team.html", None, 200, "GET", None),
    ("Judges Directory", "/hackathon/judges.html", None, 200, "GET", None),
    ("Submit GET", "/hackathon/submit.html", None, 200, "GET", None),

    # T1
    ("Submit POST (deadline blocked)", "/hackathon/submit", {"Cookie": "session=dogfood_cookie_participant_2026"}, 403, "POST", {"title": "test", "summary": "probe"}),

    # T2
    ("Judge A own scores", "/judge/scores/judge_a", {"Cookie": "session=dogfood_cookie_judge_a_2026"}, 200, "GET", None),
    ("Judge B peer probe (blocked)", "/judge/scores/judge_a", {"Cookie": "session=dogfood_cookie_judge_b_2026"}, 403, "GET", None),
    ("Participant judge scores (blocked)", "/judge/scores/judge_a", {"Cookie": "session=dogfood_cookie_participant_2026"}, 403, "GET", None),
    ("Organizer CSV export", "/export/csv", {"Cookie": "session=dogfood_cookie_organizer_2026"}, 200, "GET", None),

    # T3
    ("Community Voting (T3)", "/api/vote", None, 200, "POST", {"project_id": "prj_01", "voter_email": unique_email}),
    ("Duplicate Vote Block (T3)", "/api/vote", None, 409, "POST", {"project_id": "prj_02", "voter_email": unique_email}),
    ("Project Comments (T3)", "/api/projects/prj_01/comments", None, 200, "POST", {"author": "Tester", "comment": "Nice work!"}),
    ("Randomized Ballot (T3)", "/api/ballot", None, 200, "GET", None),
    ("Voting Page View (T3)", "/hackathon/vote.html", None, 200, "GET", None),

    # T4
    ("REST API Projects (T4)", "/api/v1/projects", None, 200, "GET", None),
    ("REST API Tracks (T4)", "/api/v1/tracks", None, 200, "GET", None),
    ("Certificate Generator (T4)", "/api/v1/certificate?project=prj_01", None, 200, "GET", None),
    ("Bulk DB Export (T4)", "/api/v1/export", {"Cookie": "session=dogfood_cookie_organizer_2026"}, 200, "GET", None),
    ("Embeddable Widget (T4)", "/embed/gallery", None, 200, "GET", None),
]

all_passed = True
for name, path, hdrs, expected_status, method, body in tests:
    status, content = test_url(path, hdrs, method, body)
    ok = (status == expected_status)
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name:35} -> got {status}, expected {expected_status}")
    if not ok:
        all_passed = False
        print(f"       Detail: {content[:200]}")

print()
if all_passed:
    print(f"ALL {len(tests)} ENDPOINTS (T1, T2, T3, T4) VERIFIED AND WORKING PROPERLY!")
else:
    print("SOME ENDPOINTS FAILED")
    exit(1)
