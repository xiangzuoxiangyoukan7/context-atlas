"""test_frontmatter 自动化测试。"""

from tests.helpers import TempDirectoryTestCase
from scripts.project_kb.frontmatter import FrontMatterError, parse_document


class FrontMatterTests(TempDirectoryTestCase):
    """验证 FrontMatterTests 相关行为。"""

    def test_parse_document_returns_metadata_and_body(self) -> None:
        """验证 parse_document_returns_metadata_and_body 场景。"""

        path = self.root / "F01.md"
        path.write_text(
            "---\nid: F01\nsources: [SRC-001, SRC-002]\n---\n# Feature\n",
            encoding="utf-8",
        )

        record = parse_document(path)

        self.assertEqual(
            record.metadata,
            {"id": "F01", "sources": ["SRC-001", "SRC-002"]},
        )
        self.assertEqual(record.body, "# Feature\n")

    def test_parse_document_rejects_nested_yaml(self) -> None:
        """验证 parse_document_rejects_nested_yaml 场景。"""

        path = self.root / "bad.md"
        path.write_text("---\nsource:\n  type: user\n---\n", encoding="utf-8")

        with self.assertRaisesRegex(
            FrontMatterError,
            "nested metadata is unsupported",
        ):
            parse_document(path)

    def test_parse_document_rejects_duplicate_keys(self) -> None:
        """验证 parse_document_rejects_duplicate_keys 场景。"""

        path = self.root / "duplicate.md"
        path.write_text("---\nid: F01\nid: F02\n---\n", encoding="utf-8")

        with self.assertRaisesRegex(FrontMatterError, "duplicate metadata key"):
            parse_document(path)
