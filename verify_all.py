import urllib.request
import urllib.error
import json

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

tests = [
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
    ("Submit POST (deadline blocked)", "/hackathon/submit", {"Cookie": "session=dogfood_cookie_participant_2026"}, 403, "POST", {"title": "test", "summary": "probe"}),
    ("Judge A own scores", "/judge/scores/judge_a", {"Cookie": "session=dogfood_cookie_judge_a_2026"}, 200, "GET", None),
    ("Judge B peer probe (blocked)", "/judge/scores/judge_a", {"Cookie": "session=dogfood_cookie_judge_b_2026"}, 403, "GET", None),
    ("Participant judge scores (blocked)", "/judge/scores/judge_a", {"Cookie": "session=dogfood_cookie_participant_2026"}, 403, "GET", None),
    ("Organizer CSV export", "/export/csv", {"Cookie": "session=dogfood_cookie_organizer_2026"}, 200, "GET", None),
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
    print("ALL 17 ENDPOINTS VERIFIED AND WORKING PROPERLY!")
else:
    print("SOME ENDPOINTS FAILED")
    exit(1)
