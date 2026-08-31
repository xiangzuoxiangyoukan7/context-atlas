"""规格就绪度与 Delta 校验测试。"""

from pathlib import Path

from scripts.project_kb.frontmatter import parse_document
from scripts.project_kb.model import DocumentRecord
from scripts.project_kb.specification import validate_specifications
from tests.helpers import TempDirectoryTestCase


class SpecificationValidationTests(TempDirectoryTestCase):
    """验证规格就绪度、验收覆盖和 Delta 条件规则。"""

    def record(self, name: str, metadata: str, body: str = "") -> DocumentRecord:
        """写入并解析一份隔离的规格记录。"""

        path = self.root / name
        path.write_text(f"---\n{metadata}\n---\n{body}", encoding="utf-8")
        return parse_document(path)

    def test_ready_specification_cannot_retain_blockers(self) -> None:
        """就绪规格不得继续保留阻塞问题。"""

        record = self.record(
            "feature.md",
            "id: F01\ntype: feature\nspec_readiness: ready\nblocking_questions: [Q-F01-001]",
        )
        self.assertIn("KB_SPEC_READY_BLOCKED", [item.code for item in validate_specifications([record])])

    def test_removed_delta_requires_migration_and_existing_change(self) -> None:
        """删除增量必须指向变更并提供真实迁移信息。"""

        target = self.record("target.md", "id: F01\ntype: feature")
        delta = self.record(
            "delta.md",
            "id: DELTA-CHG-1\ntype: specification_delta\nchange_id: CHG-1\ntarget_id: F01\noperation: removed\nreason: 待确认\nmigration: 待确认\nrollback: 待确认",
            "## REMOVED Requirements\n",
        )
        codes = {item.code for item in validate_specifications([target, delta])}
        self.assertIn("KB_DELTA_CHANGE", codes)
        self.assertIn("KB_DELTA_MIGRATION", codes)

    def test_ready_feature_requires_normative_embedded_scenario(self) -> None:
        """就绪功能必须声明并内嵌完整验收场景。"""

        feature = self.record(
            "feature.md",
            "id: F01\ntype: feature\nspec_readiness: ready\nblocking_questions: []",
            "# Feature\n",
        )
        codes = [item.code for item in validate_specifications([feature])]
        self.assertIn("KB_SPEC_COVERAGE", codes)
        self.assertIn("KB_SPEC_NORMATIVE", codes)
        self.assertIn("KB_SPEC_SCENARIO", codes)
        self.assertEqual(5, codes.count("KB_SPEC_FEATURE_DESIGN"))

    def test_interface_requires_business_name_and_single_endpoint(self) -> None:
        """接口文件必须可读，且不能聚合多个 HTTP 端点。"""

        interface = self.record(
            "API-001.md",
            "id: API-001\ntype: interface\ntitle: API-001\ninterface_kind: http",
            "| 方法 | 路径 |\n| --- | --- |\n| GET | /one |\n| POST | /two |\n",
        )
        codes = {item.code for item in validate_specifications([interface])}
        self.assertIn("KB_INTERFACE_NAME", codes)
        self.assertIn("KB_INTERFACE_AGGREGATE", codes)

    def test_external_task_requires_traceability_and_verification(self) -> None:
        """外部任务必须可回溯到功能或变更并说明验证方式。"""

        task = self.record(
            "task.md",
            "id: TASK-F01-001\ntype: task\nfeature: F01\nacceptance: [F01-AC-01]",
            "# Task\n",
        )

        codes = {item.code for item in validate_specifications([task])}

        self.assertIn("KB_COVERAGE_TASK_ORIGIN", codes)
        self.assertIn("KB_COVERAGE_TASK_VERIFICATION", codes)
