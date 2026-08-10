from pathlib import Path

from scripts.project_kb.validator import ValidationConfig, validate
from tests.helpers import (
    TempDirectoryTestCase,
    make_valid_knowledge_base,
    write_record,
)


class LifecycleValidationTests(TempDirectoryTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.knowledge_base = make_valid_knowledge_base(self.root / "doc-example")
        self.config = ValidationConfig(schema_root=Path("schemas"))

    def test_approved_item_requires_approval_metadata(self) -> None:
        write_record(
            self.knowledge_base / "01-功能基线" / "approved.md",
            {
                "id": "KNOWLEDGE-001",
                "type": "knowledge_item",
                "title": "Approved knowledge",
                "status": "approved",
                "version": "1.0.0",
                "sources": ["SRC-001"],
                "last_updated": "2026-08-10",
            },
        )

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_APPROVAL_REQUIRED", codes)

    def test_conflicted_item_requires_two_distinct_sources(self) -> None:
        write_record(
            self.knowledge_base / "02-架构与契约" / "conflict.md",
            {
                "id": "CONFLICT-001",
                "type": "knowledge_item",
                "title": "Runtime conflict",
                "status": "conflicted",
                "version": "1.0.0",
                "sources": ["SRC-001"],
                "resolution_required_from": "project_owner",
                "last_updated": "2026-08-10",
            },
        )

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_CONFLICT_SOURCES", codes)

    def test_conflicted_item_requires_named_resolver(self) -> None:
        write_record(
            self.knowledge_base / "02-架构与契约" / "conflict.md",
            {
                "id": "CONFLICT-001",
                "type": "knowledge_item",
                "title": "Runtime conflict",
                "status": "conflicted",
                "version": "1.0.0",
                "sources": ["SRC-001", "SRC-002"],
                "last_updated": "2026-08-10",
            },
        )

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_CONFLICT_RESOLVER", codes)

    def test_superseded_item_requires_bidirectional_replacement_link(self) -> None:
        write_record(
            self.knowledge_base / "02-架构与契约/old.md",
            {
                "id": "KNOWLEDGE-OLD",
                "type": "knowledge_item",
                "title": "Old decision",
                "status": "superseded",
                "version": "1.0.0",
                "sources": ["SRC-001"],
                "last_updated": "2026-08-10",
            },
        )
        write_record(
            self.knowledge_base / "02-架构与契约/new.md",
            {
                "id": "KNOWLEDGE-NEW",
                "type": "knowledge_item",
                "title": "New decision",
                "status": "approved",
                "version": "2.0.0",
                "sources": ["SRC-002"],
                "approved_by": "project-owner",
                "approved_at": "2026-08-10",
                "supersedes": ["KNOWLEDGE-OLD"],
                "last_updated": "2026-08-10",
            },
        )

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_SUPERSESSION_LINK", codes)
