import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import app


class DogfoodPortalTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.init_db()

    def setUp(self):
        self.client = app.app.test_client()

    # --- T1 Tests ---
    def test_gallery_public_accessible(self):
        resp = self.client.get("/hackathon/gallery.html")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Glass Signal", resp.data)
        self.assertIn(b"Small Meadow", resp.data)
        self.assertIn(b"Deep Compass", resp.data)

    def test_closed_event_blocks_submissions(self):
        self.client.set_cookie("session", "dogfood_cookie_participant_2026")
        resp = self.client.post(
            "/hackathon/submit",
            json={"title": "probe", "summary": "test"},
        )
        self.assertEqual(resp.status_code, 403)

    # --- T2 Tests ---
    def test_judge_reads_own_scores(self):
        self.client.set_cookie("session", "dogfood_cookie_judge_a_2026")
        resp = self.client.get("/judge/scores/judge_a")
        self.assertEqual(resp.status_code, 200)

    def test_judge_cannot_read_peer_scores(self):
        self.client.set_cookie("session", "dogfood_cookie_judge_b_2026")
        resp = self.client.get("/judge/scores/judge_a")
        self.assertEqual(resp.status_code, 403)

    def test_participant_blocked_from_judge_scores(self):
        self.client.set_cookie("session", "dogfood_cookie_participant_2026")
        resp = self.client.get("/judge/scores/judge_a")
        self.assertEqual(resp.status_code, 403)

    def test_organizer_can_export_csv(self):
        self.client.set_cookie("session", "dogfood_cookie_organizer_2026")
        resp = self.client.get("/export/csv")
        self.assertEqual(resp.status_code, 200)
        lines = resp.data.decode("utf-8").splitlines()
        self.assertGreater(len(lines), 1)
        self.assertIn(",", lines[0])

    # --- T3 Tests ---
    def test_community_voting_and_duplicate_prevention(self):
        email = "unique_voter_123@example.org"
        resp = self.client.post(
            "/api/vote",
            json={"project_id": "prj_01", "voter_email": email},
        )
        self.assertEqual(resp.status_code, 200)
        # Duplicate should be blocked with 409
        dup_resp = self.client.post(
            "/api/vote",
            json={"project_id": "prj_02", "voter_email": email},
        )
        self.assertEqual(dup_resp.status_code, 409)

    def test_project_comments(self):
        resp = self.client.post(
            "/api/projects/prj_01/comments",
            json={"author": "Unit Tester", "comment": "Excellent project!"},
        )
        self.assertEqual(resp.status_code, 200)
        get_resp = self.client.get("/api/projects/prj_01/comments")
        self.assertEqual(get_resp.status_code, 200)
        self.assertIn(b"Excellent project!", get_resp.data)

    def test_randomized_ballot(self):
        resp = self.client.get("/api/ballot")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["total_projects"], 41)

    # --- T4 Tests ---
    def test_rest_api_projects(self):
        resp = self.client.get("/api/v1/projects")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["count"], 41)

    def test_certificate_generation(self):
        resp = self.client.get("/api/v1/certificate?project=prj_01")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("certificate_id", data)
        self.assertIn("cryptographic_signature", data)

    def test_bulk_export(self):
        self.client.set_cookie("session", "dogfood_cookie_organizer_2026")
        resp = self.client.get("/api/v1/export")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("projects", data)
        self.assertIn("teams", data)


if __name__ == "__main__":
    unittest.main()
