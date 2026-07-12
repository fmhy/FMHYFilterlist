import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_redirects


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class BuildRedirectsTests(unittest.TestCase):
    def test_normalize_url_preserves_paths_and_removes_fragments(self):
        self.assertEqual(
            build_redirects.normalize_url(
                "HTTPS://Example.COM/path/?query=value#section"
            ),
            "https://example.com/path?query=value",
        )
        self.assertEqual(
            build_redirects.normalize_url(
                "https://example.com/path?item=1&utm_source=wiki&fbclid=tracking"
            ),
            "https://example.com/path?item=1",
        )

    def test_private_network_urls_are_rejected(self):
        for url in ("http://127.0.0.1/admin", "http://[::1]/", "http://localhost/"):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    build_redirects.assert_public_url(url)

    def test_extract_wiki_urls_reads_all_links_from_resource_lines(self):
        markdown = """
* ⭐ **[Primary](https://old.example/path)** / [Mirror](https://mirror.example/)
* Plain note with [incidental link](https://ignored.example/)
* ↪️ **[Internal](https://fmhy.net/beginners-guide)**
"""

        self.assertEqual(
            build_redirects.extract_wiki_urls(markdown),
            ["https://mirror.example/", "https://old.example/path"],
        )

    def test_generate_candidates_omits_unchanged_urls_and_sorts_results(self):
        sources = [
            "https://second.example/old",
            "https://same.example/",
            "https://first.example/old",
        ]
        destinations = {
            sources[0]: "https://destination.example/two/",
            sources[1]: "https://same.example/",
            sources[2]: "https://destination.example/one",
        }

        candidates = build_redirects.generate_candidates(
            sources, resolver=destinations.__getitem__
        )

        self.assertEqual(
            candidates,
            [
                {
                    "source": "https://first.example/old",
                    "target": "https://destination.example/one",
                },
                {
                    "source": "https://second.example/old",
                    "target": "https://destination.example/two",
                },
            ],
        )

    def test_generate_candidates_omits_same_site_and_known_service_redirects(self):
        destinations = {
            "https://app.example.com": "https://login.example.com/sign-in",
            "https://discord.gg/example": "https://discord.com/invite/example",
            "https://redd.it/example": "https://reddit.com/comments/example",
            "https://video.example/a": "https://accounts.google.com/signin",
        }

        self.assertEqual(
            build_redirects.generate_candidates(
                destinations, resolver=destinations.__getitem__
            ),
            [],
        )

    def test_generate_candidates_omits_https_to_http_downgrades(self):
        self.assertEqual(
            build_redirects.generate_candidates(
                ["https://secure.example/resource"],
                resolver=lambda _: "http://different.example/resource",
            ),
            [],
        )

    def test_published_aliases_contain_only_manually_approved_pairs(self):
        aliases = json.loads(
            (REPOSITORY_ROOT / "filterlist-redirects.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            aliases,
            [
                {
                    "source": "https://alienflix.net",
                    "target": "https://hdtodayz.net",
                }
            ],
        )

    def test_approved_exact_pairs_are_removed_from_candidates(self):
        candidates = [
            {"source": "https://old.example", "target": "https://new.example"},
            {"source": "https://changed.example", "target": "https://newer.example"},
        ]
        approved = [
            {"source": "https://old.example", "target": "https://new.example"},
            {"source": "https://changed.example", "target": "https://previous.example"},
        ]

        self.assertEqual(
            build_redirects.remove_approved_candidates(candidates, approved),
            [
                {
                    "source": "https://changed.example",
                    "target": "https://newer.example",
                }
            ],
        )

    def test_scan_candidates_keeps_successes_and_reports_failures(self):
        def resolver(source):
            if "broken" in source:
                raise OSError("connection failed")
            return "https://new.example/path"

        candidates, failures = build_redirects.scan_candidates(
            ["https://old.example", "https://broken.example"],
            resolver=resolver,
            workers=2,
        )

        self.assertEqual(
            candidates,
            [{"source": "https://old.example", "target": "https://new.example/path"}],
        )
        self.assertEqual(
            failures,
            [{"source": "https://broken.example", "error": "connection failed"}],
        )

    def test_main_writes_candidate_json_from_wiki_export(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output_file = root / "filterlist-redirect-candidates.json"
            errors_file = root / "filterlist-redirect-errors.json"

            with patch.object(build_redirects, "fetch_wiki", return_value=(
                "* ⭐ **[AlienFlix](https://alienflix.net/)**"
            )), patch.object(build_redirects, "resolve_redirect", return_value=(
                "https://hdtodayz.net/"
            )):
                result = build_redirects.main(
                    [
                        "--output", str(output_file),
                        "--errors-output", str(errors_file),
                        "--approved-file", str(root / "missing-approved.json"),
                        "--workers", "1",
                    ]
                )

            self.assertEqual(result, 0)
            self.assertEqual(
                json.loads(output_file.read_text(encoding="utf-8")),
                [
                    {
                        "source": "https://alienflix.net",
                        "target": "https://hdtodayz.net",
                    }
                ],
            )
            self.assertEqual(json.loads(errors_file.read_text(encoding="utf-8")), [])


if __name__ == "__main__":
    unittest.main()
