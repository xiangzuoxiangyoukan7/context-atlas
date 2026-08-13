"""test_invalid_fixtures 自动化测试。"""

from pathlib import Path
import tempfile
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
    "relation-unknown-field": "KB_REL_FIELD_UNKNOWN",
    "relation-broken-target": "KB_REL_TARGET_FILE",
    "relation-wrong-direction": "KB_REL_DIRECTION",
}


class InvalidFixtureTests(unittest.TestCase):
    """验证 InvalidFixtureTests 相关行为。"""

    def test_each_fixture_has_one_exact_intended_error(self) -> None:
        """验证 each_fixture_has_one_exact_intended_error 场景。"""

        config = ValidationConfig(schema_root=Path("schemas"))
        for name, expected_code in FIXTURES.items():
            with self.subTest(name=name):
                root = Path("tests/fixtures/invalid") / name
                readme = (root / "README.md").read_text(encoding="utf-8")
                codes = {issue.code for issue in validate(root, config)}

                self.assertIn(f"expected_code: {expected_code}", readme)
                self.assertEqual(codes, {expected_code})

    def test_invalid_relation_catalog_has_stable_issue(self) -> None:
        """关系目录缺失时应返回稳定问题，而不是向用户暴露异常堆栈。"""

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            missing_catalog = root / "missing-relation-catalog.json"
            issues = validate(
                root,
                ValidationConfig(
                    schema_root=Path("schemas"),
                    relation_catalog_path=missing_catalog,
                ),
            )

        self.assertEqual(["KB_REL_CATALOG"], [issue.code for issue in issues])


if __name__ == "__main__":
    unittest.main()
