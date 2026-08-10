from pathlib import Path
import unittest

from scripts.project_kb.validator import ValidationConfig, validate


FIXTURES = {
    "stale-proposal": "KB_PROPOSAL_STALE",
    "missing-approval": "KB_APPROVAL_REQUIRED",
    "unresolved-conflict": "KB_CONFLICT_RESOLVER",
    "broken-traceability": "KB_TRACE_REFERENCE",
    "sensitive-material": "KB_SENSITIVE_VALUE",
    "archived-reference": "KB_TRACE_REFERENCE",
    "source-wrong-type": "KB_SOURCE_TYPE",
    "ai-inference-approval": "KB_APPROVAL_AI_INFERENCE",
    "one-way-supersession": "KB_SUPERSESSION_LINK",
}


class InvalidFixtureTests(unittest.TestCase):
    def test_each_fixture_has_one_exact_intended_error(self) -> None:
        config = ValidationConfig(schema_root=Path("schemas"))
        for name, expected_code in FIXTURES.items():
            with self.subTest(name=name):
                root = Path("tests/fixtures/invalid") / name
                readme = (root / "README.md").read_text(encoding="utf-8")
                codes = {issue.code for issue in validate(root, config)}

                self.assertIn(f"expected_code: {expected_code}", readme)
                self.assertEqual(codes, {expected_code})


if __name__ == "__main__":
    unittest.main()
