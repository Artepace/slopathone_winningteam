import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("github_sources", Path(__file__).resolve().parents[1] / "github_sources.py")
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


def solution_zip(readme="Version one", instruction="Play safely", skill="Do the task"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("solution/manifest.json", json.dumps({"team": "Winning team", "mode": "agent", "instruction": instruction}))
        archive.writestr("solution/README.md", readme)
        archive.writestr("solution/design/skills_design.md", "Design")
        archive.writestr("solution/design/decision_report.md", "Report")
        archive.writestr("solution/skills/test/SKILL.md", "---\nname: test\ndescription: Test\n---\n" + skill)
    return buffer.getvalue()


class GithubSourceTests(unittest.TestCase):
    def test_reject_incomplete_tree(self):
        with self.assertRaises(ValueError):
            source.solution_entries({"truncated": True})

    def test_reject_unsafe_path(self):
        with self.assertRaises(ValueError):
            source.solution_entries({"tree": [{"type": "blob", "path": "../solution.zip", "sha": "a" * 40}]})

    def test_download_hash_and_seen_are_content_based(self):
        data = solution_zip()
        blob = source.blob_sha(data)
        commit = {"sha": "a" * 40, "commit": {"committer": {"date": "2026-10-29T18:00:00Z"}}}
        tree = {"tree": [{"type": "blob", "path": "v4_solution.zip", "sha": blob, "size": len(data)}]}
        def response(url):
            return tree if "/git/trees/" in url else commit
        with tempfile.TemporaryDirectory() as temp, patch.object(source, "fetch_json", side_effect=response), patch.object(source, "fetch", return_value=data):
            first = source.check("owner/repo", "main", temp, True)
            second = source.check("owner/repo", "main", temp, True)
            self.assertTrue(first["archives"][0]["is_new"])
            self.assertFalse(second["archives"][0]["is_new"])
            item = second["archives"][0]
            self.assertEqual(item["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(Path(item["local_path"]).read_bytes(), data)
            self.assertEqual(first["archives"][0]["gameplay_sha256"], item["gameplay_sha256"])
            self.assertEqual(item["gameplay_duplicate_of"], [])

    def test_documents_only_revision_is_gameplay_duplicate(self):
        data = [solution_zip(readme="Old documentation"), solution_zip(readme="Corrected documentation")]
        commits = ["a" * 40, "b" * 40]
        with tempfile.TemporaryDirectory() as temp:
            checks = []
            for payload, sha in zip(data, commits):
                commit = {"sha": sha, "commit": {"committer": {"date": "2026-10-29T18:00:00Z"}}}
                tree = {"tree": [{"type": "blob", "path": "solution.zip", "sha": source.blob_sha(payload), "size": len(payload)}]}
                with patch.object(source, "fetch_json", side_effect=[commit, tree]), patch.object(source, "fetch", return_value=payload):
                    checks.append(source.check("owner/repo", "main", temp, True)["archives"][0])
            self.assertNotEqual(checks[0]["sha256"], checks[1]["sha256"])
            self.assertNotEqual(checks[0]["content_sha256"], checks[1]["content_sha256"])
            self.assertEqual(checks[0]["gameplay_sha256"], checks[1]["gameplay_sha256"])
            self.assertTrue(checks[1]["is_new"])
            self.assertEqual(checks[1]["gameplay_duplicate_of"][0]["commit"], commits[0])
            stored = json.loads((Path(temp) / "github-index.json").read_text())
            self.assertTrue(all(item.get("gameplay_sha256") for item in stored["downloads"].values()))

    def test_instruction_or_skill_changes_gameplay_fingerprint(self):
        with tempfile.TemporaryDirectory() as temp:
            original = source.archive_fingerprints(solution_zip(), temp)["gameplay_sha256"]
            changed_instruction = source.archive_fingerprints(solution_zip(instruction="Different strategy"), temp)["gameplay_sha256"]
            changed_skill = source.archive_fingerprints(solution_zip(skill="Different skill"), temp)["gameplay_sha256"]
            self.assertNotEqual(original, changed_instruction)
            self.assertNotEqual(original, changed_skill)

    def test_bad_archive_does_not_publish_download(self):
        payload = b"not a zip"
        commit = {"sha": "a" * 40, "commit": {"committer": {"date": "x"}}}
        tree = {"tree": [{"type": "blob", "path": "solution.zip", "sha": source.blob_sha(payload)}]}
        with tempfile.TemporaryDirectory() as temp, patch.object(source, "fetch_json", side_effect=[commit, tree]), patch.object(source, "fetch", return_value=payload):
            with self.assertRaises(ValueError):
                source.check("owner/repo", "main", temp, True)
            self.assertFalse(list(Path(temp).glob("*.zip")))

    def test_bad_blob_does_not_publish_download(self):
        commit = {"sha": "a" * 40, "commit": {"committer": {"date": "x"}}}
        tree = {"tree": [{"type": "blob", "path": "solution.zip", "sha": "b" * 40}]}
        with tempfile.TemporaryDirectory() as temp, patch.object(source, "fetch_json", side_effect=[commit, tree]), patch.object(source, "fetch", return_value=b"wrong"):
            with self.assertRaises(ValueError):
                source.check("owner/repo", "main", temp, True)
            self.assertFalse(list(Path(temp).glob("*.zip")))


if __name__ == "__main__":
    unittest.main()
