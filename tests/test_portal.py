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


if __name__ == "__main__":
    unittest.main()
