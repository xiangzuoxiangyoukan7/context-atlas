"""test_security 自动化测试。"""

from pathlib import Path

from scripts.project_kb.reporting import render_text
from scripts.project_kb.validator import ValidationConfig, validate
from tests.helpers import TempDirectoryTestCase, make_valid_knowledge_base, write_record


class SecurityTests(TempDirectoryTestCase):
    """验证 SecurityTests 相关行为。"""

    def test_token_assignment_is_reported_without_echoing_secret(self) -> None:
        """验证 token_assignment_is_reported_without_echoing_secret 场景。"""

        knowledge_base = make_valid_knowledge_base(self.root / "doc-example")
        write_record(
            knowledge_base / "05-开发指南" / "unsafe.md",
            {
                "id": "SECURITY-001",
                "type": "knowledge_item",
                "title": "Unsafe example",
                "status": "proposed",
                "version": "1.0.0",
                "sources": ["SRC-001"],
                "last_updated": "2026-08-10",
            },
            body="# Unsafe\n\nSERVICE_TOKEN=super-secret-value\n",
        )

        issues = validate(
            knowledge_base,
            ValidationConfig(schema_root=Path("schemas")),
        )
        security_issues = [issue for issue in issues if issue.code == "KB_SENSITIVE_VALUE"]

        self.assertEqual(len(security_issues), 1)
        self.assertNotIn("super-secret-value", security_issues[0].message)

    def test_environment_placeholder_is_allowed(self) -> None:
        """验证 environment_placeholder_is_allowed 场景。"""

        knowledge_base = make_valid_knowledge_base(self.root / "doc-example")
        write_record(
            knowledge_base / "05-开发指南" / "safe.md",
            {
                "id": "SECURITY-001",
                "type": "knowledge_item",
                "title": "Safe example",
                "status": "proposed",
                "version": "1.0.0",
                "sources": ["SRC-001"],
                "last_updated": "2026-08-10",
            },
            body="# Safe\n\nSERVICE_TOKEN=${SERVICE_TOKEN}\n",
        )

        codes = {
            issue.code
            for issue in validate(
                knowledge_base,
                ValidationConfig(schema_root=Path("schemas")),
            )
        }

        self.assertNotIn("KB_SENSITIVE_VALUE", codes)

    def test_sensitive_front_matter_value_is_reported_without_echo(self) -> None:
        """验证 sensitive_front_matter_value_is_reported_without_echo 场景。"""

        knowledge_base = make_valid_knowledge_base(self.root / "doc-example")
        path = knowledge_base / "00-项目总览/secret.md"
        write_record(
            path,
            {
                "id": "SECRET-META",
                "type": "knowledge_item",
                "title": "Secret metadata",
                "status": "proposed",
                "version": "1.0.0",
                "sources": ["SRC-001"],
                "API_TOKEN": "top-secret-value",
                "last_updated": "2026-08-10",
            },
        )

        issues = validate(
            knowledge_base,
            ValidationConfig(schema_root=Path("schemas")),
        )
        report = render_text(issues)

        self.assertIn("KB_SENSITIVE_VALUE", {issue.code for issue in issues})
        self.assertNotIn("top-secret-value", report)
