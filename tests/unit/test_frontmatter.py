from tests.helpers import TempDirectoryTestCase
from scripts.project_kb.frontmatter import FrontMatterError, parse_document


class FrontMatterTests(TempDirectoryTestCase):
    def test_parse_document_returns_metadata_and_body(self) -> None:
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
        path = self.root / "bad.md"
        path.write_text("---\nsource:\n  type: user\n---\n", encoding="utf-8")

        with self.assertRaisesRegex(
            FrontMatterError,
            "nested metadata is unsupported",
        ):
            parse_document(path)

    def test_parse_document_rejects_duplicate_keys(self) -> None:
        path = self.root / "duplicate.md"
        path.write_text("---\nid: F01\nid: F02\n---\n", encoding="utf-8")

        with self.assertRaisesRegex(FrontMatterError, "duplicate metadata key"):
            parse_document(path)
