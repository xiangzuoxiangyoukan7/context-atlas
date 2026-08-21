"""test_traceability 自动化测试。"""

from pathlib import Path

from scripts.project_kb.validator import ValidationConfig, validate
from tests.helpers import TempDirectoryTestCase, make_valid_knowledge_base, write_record


class TraceabilityTests(TempDirectoryTestCase):
    """验证 TraceabilityTests 相关行为。"""

    def setUp(self) -> None:
        """初始化当前测试所需的隔离环境。"""

        super().setUp()
        self.knowledge_base = make_valid_knowledge_base(self.root / "doc-example")
        self.config = ValidationConfig(schema_root=Path("schemas"))

    def test_feature_reference_to_unknown_contract_is_rejected(self) -> None:
        """验证 feature_reference_to_unknown_contract_is_rejected 场景。"""

        write_record(
            self.knowledge_base / "01-功能基线" / "F01.md",
            {
                "id": "F01",
                "type": "feature",
                "title": "Feature",
                "status": "baselined",
                "phase": "mvp",
                "priority": "P0",
                "current_slice": "included",
                "depends_on": [],
                "acceptance": ["F01-AC-01"],
                "contracts": ["CONTRACT-404"],
                "adr": [],
                "last_updated": "2026-08-10",
            },
        )
        (self.knowledge_base / "03-变更与证据" / "验收矩阵.md").write_text(
            "# 验收矩阵\n\n"
            "| 验收编号 | 对象 | 条件摘要 | 结果 | 证据位置 | 对应版本 |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| F01-AC-01 | F01 | condition | not_started | — | — |\n",
            encoding="utf-8",
        )

        issues = validate(self.knowledge_base, self.config)

        self.assertIn(
            ("KB_TRACE_REFERENCE", "unknown contracts reference: CONTRACT-404"),
            {(issue.code, issue.message) for issue in issues},
        )

    def test_source_reference_must_resolve(self) -> None:
        """验证 source_reference_must_resolve 场景。"""

        write_record(
            self.knowledge_base / "01-功能基线" / "knowledge.md",
            {
                "id": "KNOWLEDGE-001",
                "type": "knowledge_item",
                "title": "Knowledge",
                "status": "proposed",
                "version": "1.0.0",
                "sources": ["SRC-404"],
                "last_updated": "2026-08-10",
            },
        )

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_SOURCE_UNKNOWN", codes)

    def test_task_feature_reference_must_resolve(self) -> None:
        """验证 task_feature_reference_must_resolve 场景。"""

        write_record(
            self.knowledge_base / "03-变更与证据/任务包/TASK-F99-001.md",
            {
                "id": "TASK-F99-001",
                "type": "task",
                "title": "Unknown feature task",
                "feature": "F99",
                "status": "ready",
                "acceptance": ["F99-AC-01"],
                "last_updated": "2026-08-10",
            },
        )

        messages = [
            issue.message
            for issue in validate(self.knowledge_base, self.config)
            if issue.code == "KB_TRACE_REFERENCE"
        ]

        self.assertIn("unknown feature reference: F99", messages)

    def test_domain_references_must_resolve(self) -> None:
        """验证 domain_references_must_resolve 场景。"""

        write_record(
            self.knowledge_base / "01-功能基线/F01.md",
            {
                "id": "F01",
                "type": "feature",
                "title": "Feature",
                "status": "baselined",
                "phase": "mvp",
                "priority": "P0",
                "current_slice": "included",
                "depends_on": [],
                "acceptance": ["F01-AC-01"],
                "contracts": [],
                "adr": [],
                "database": ["DB-UNKNOWN"],
                "prototypes": ["PROTO-UNKNOWN"],
                "external_dependencies": ["EXT-UNKNOWN"],
                "last_updated": "2026-08-10",
            },
        )

        messages = {
            issue.message
            for issue in validate(self.knowledge_base, self.config)
            if issue.code == "KB_TRACE_REFERENCE"
        }

        self.assertEqual(
            {
                "unknown database reference: DB-UNKNOWN",
                "unknown prototypes reference: PROTO-UNKNOWN",
                "unknown external_dependencies reference: EXT-UNKNOWN",
            },
            messages,
        )

    def test_passed_acceptance_requires_resolvable_current_evidence(self) -> None:
        """通过项的证据名称必须唯一解析到当前验收证据文件。"""

        write_record(
            self.knowledge_base / "01-功能基线/F01.md",
            {
                "id": "F01",
                "type": "feature",
                "title": "Feature",
                "status": "baselined",
                "phase": "mvp",
                "priority": "P0",
                "current_slice": "included",
                "depends_on": [],
                "acceptance": ["F01-AC-01"],
                "contracts": [],
                "adr": [],
                "last_updated": "2026-08-10",
            },
        )
        matrix = self.knowledge_base / "03-变更与证据/验收矩阵.md"
        matrix.write_text(
            "# 验收矩阵\n\n"
            "| 验收编号 | 对象 | 条件摘要 | 结果 | 证据位置 | 对应版本 |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| F01-AC-01 | F01 | condition | passed | 不存在证据 | v1 |\n",
            encoding="utf-8",
        )

        codes = {issue.code for issue in validate(self.knowledge_base, self.config)}

        self.assertIn("KB_COVERAGE_EVIDENCE_PATH", codes)
