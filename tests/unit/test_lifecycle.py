from pathlib import Path

from scripts.project_kb.validator import ValidationConfig, validate
from tests.helpers import (
    TempDirectoryTestCase,
    make_valid_knowledge_base,
    write_record,
)


class TechnologyStackModelTests(TempDirectoryTestCase):
    def test_single_and_multi_stack_projects_share_one_core_structure(self) -> None:
        cases = {
            "single": "| Java | 21 | app | Spring Boot service | mvn test | application.yml | SRC-001 | approved |",
            "multi": "| Spring Boot | 3.x | backend | API | mvn test | application.yml | SRC-001 | approved |\n| Python | 3.12 | tools | data job | pytest | pyproject.toml | SRC-002 | approved |\n| Vue | 3.x | web | frontend | npm test | package.json | SRC-001 | approved |",
        }
        for name, rows in cases.items():
            with self.subTest(name=name):
                root = self.root / name / f"doc-{name}"
                root.parent.mkdir(parents=True)
                from tests.helpers import materialize_core_template

                root = materialize_core_template(root.parent, name)
                technology = root / "00-项目总览" / "技术栈与版本.md"
                content = technology.read_text(encoding="utf-8").replace(
                    "| 待确认 | 待确认 | 待确认 | 待确认 | 待确认 | 待确认 | SRC-001 | missing |",
                    rows,
                )
                technology.write_text(content, encoding="utf-8")
                self.assertEqual(validate(root, ValidationConfig(schema_root=Path("schemas"))), [])
                self.assertFalse((root / ".project-kb" / "profiles").exists())


class LifecycleValidationTests(TempDirectoryTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.knowledge_base = make_valid_knowledge_base(self.root / "doc-example")
        self.config = ValidationConfig(schema_root=Path("schemas"))

    def write_data_asset(
        self,
        identifier: str = "DATA-001",
        **overrides: object,
    ) -> Path:
        metadata: dict[str, object] = {
            "id": identifier,
            "type": "data_asset",
            "title": "客户信息",
            "status": "approved",
            "version": "1.0.0",
            "sources": ["SRC-001"],
            "owner": "project-owner",
            "source_types": ["database"],
            "sensitivity": "internal",
            "retention": "project-lifetime",
            "last_updated": "2026-08-10",
        }
        metadata.update(overrides)
        return write_record(
            self.knowledge_base / f"02-架构与契约/数据资产/{identifier}.md",
            metadata,
        )

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

    def test_approved_item_rejects_confirmation_for_stale_proposal(self) -> None:
        write_record(
            self.knowledge_base / "02-架构与契约/stale.md",
            {
                "id": "KNOWLEDGE-STALE",
                "type": "knowledge_item",
                "title": "Stale proposal",
                "status": "approved",
                "version": "1.0.0",
                "sources": ["SRC-001"],
                "approved_by": "project-owner",
                "approved_at": "2026-08-10",
                "proposal_revision": "2",
                "confirmed_revision": "1",
                "last_updated": "2026-08-10",
            },
        )

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_PROPOSAL_STALE", codes)

    def test_lifecycle_source_reference_requires_source_record_type(self) -> None:
        write_record(
            self.knowledge_base / "00-项目总览/not-a-source.md",
            {
                "id": "EVIDENCE-001",
                "type": "knowledge_item",
                "title": "Not a source record",
                "status": "proposed",
                "version": "1.0.0",
                "sources": ["SRC-001"],
                "last_updated": "2026-08-10",
            },
        )
        path = self.write_data_asset(
            status="proposed",
            sources=["EVIDENCE-001"],
        )

        codes = [
            issue.code
            for issue in validate(self.knowledge_base, self.config)
            if issue.path == path
        ]

        self.assertEqual(codes, ["KB_SOURCE_TYPE"])

    def test_approved_lifecycle_record_rejects_ai_inference_only_source(self) -> None:
        write_record(
            self.knowledge_base / "00-项目总览/SRC-003.md",
            {
                "id": "SRC-003",
                "type": "source",
                "title": "AI inference",
                "source_type": "ai_inference",
                "reference": "test inference",
                "last_updated": "2026-08-10",
            },
        )
        path = self.write_data_asset(
            sources=["SRC-003"],
            approved_by="project-owner",
            approved_at="2026-08-10",
        )

        codes = [
            issue.code
            for issue in validate(self.knowledge_base, self.config)
            if issue.path == path
        ]

        self.assertEqual(codes, ["KB_APPROVAL_AI_INFERENCE"])

    def test_approved_data_asset_accepts_registered_non_inference_source(self) -> None:
        path = self.write_data_asset(
            approved_by="project-owner",
            approved_at="2026-08-10",
        )

        issues = [
            issue
            for issue in validate(self.knowledge_base, self.config)
            if issue.path == path
        ]

        self.assertEqual(issues, [])

    def test_superseded_item_rejects_successor_without_reverse_reference(self) -> None:
        old_path = write_record(
            self.knowledge_base / "02-架构与契约/old-one-way.md",
            {
                "id": "KNOWLEDGE-OLD-ONE-WAY",
                "type": "knowledge_item",
                "title": "Old one-way decision",
                "status": "superseded",
                "version": "1.0.0",
                "sources": ["SRC-001"],
                "superseded_by": "KNOWLEDGE-NEW-ONE-WAY",
                "last_updated": "2026-08-10",
            },
        )
        write_record(
            self.knowledge_base / "02-架构与契约/new-one-way.md",
            {
                "id": "KNOWLEDGE-NEW-ONE-WAY",
                "type": "knowledge_item",
                "title": "New one-way decision",
                "status": "approved",
                "version": "2.0.0",
                "sources": ["SRC-002"],
                "approved_by": "project-owner",
                "approved_at": "2026-08-10",
                "last_updated": "2026-08-10",
            },
        )

        codes = [
            issue.code
            for issue in validate(self.knowledge_base, self.config)
            if issue.path == old_path
        ]

        self.assertEqual(codes, ["KB_SUPERSESSION_LINK"])

    def test_superseded_data_asset_rejects_successor_without_reverse_reference(
        self,
    ) -> None:
        old_path = self.write_data_asset(
            "DATA-001",
            status="superseded",
            superseded_by="DATA-002",
        )
        self.write_data_asset(
            "DATA-002",
            approved_by="project-owner",
            approved_at="2026-08-10",
        )

        codes = [
            issue.code
            for issue in validate(self.knowledge_base, self.config)
            if issue.path == old_path
        ]

        self.assertEqual(codes, ["KB_SUPERSESSION_LINK"])

    def test_approved_data_asset_requires_approval_metadata(self) -> None:
        self.write_data_asset()

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_APPROVAL_REQUIRED", codes)

    def test_data_asset_rejects_unknown_knowledge_source(self) -> None:
        self.write_data_asset(status="proposed", sources=["SRC-999"])

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_SOURCE_UNKNOWN", codes)

    def test_conflicted_data_asset_requires_two_sources(self) -> None:
        self.write_data_asset(
            status="conflicted",
            resolution_required_from="project-owner",
        )

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_CONFLICT_SOURCES", codes)

    def test_data_asset_rejects_broken_local_contract_link(self) -> None:
        self.write_data_asset(status="proposed")
        path = self.knowledge_base / "02-架构与契约/数据资产/DATA-001.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\n[缺失数据库契约](../数据库/DB-999.md)\n",
            encoding="utf-8",
        )

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_LINK_BROKEN", codes)
