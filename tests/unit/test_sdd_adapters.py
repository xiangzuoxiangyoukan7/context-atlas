"""外部 SDD 只读适配测试。"""

from scripts.project_kb.sdd_adapters import inspect_openspec, inspect_spec_kit
from tests.helpers import TempDirectoryTestCase


class SddAdapterTests(TempDirectoryTestCase):
    """验证外部 SDD 工件映射不会产生写入。"""

    def write(self, relative: str) -> None:
        """创建一个最小外部工件用于只读发现。"""

        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# artifact\n", encoding="utf-8")

    def test_openspec_maps_change_artifacts_without_writes(self) -> None:
        """OpenSpec 提案、增量和设计应映射到对应候选角色。"""

        self.write("openspec/changes/add-login/proposal.md")
        self.write("openspec/changes/add-login/specs/user-auth/spec.md")
        self.write("openspec/changes/add-login/design.md")
        result = inspect_openspec(self.root).to_dict()
        self.assertFalse(result["writes_performed"])
        self.assertEqual(
            {"change_proposal", "specification_delta", "change_design"},
            {item["atlas_role"] for item in result["artifacts"]},
        )

    def test_spec_kit_maps_contracts_and_checklists(self) -> None:
        """Spec Kit 契约和检查单应保留不同候选角色。"""

        self.write("specs/001-login/spec.md")
        self.write("specs/001-login/contracts/openapi.md")
        self.write("specs/001-login/checklists/requirements.md")
        result = inspect_spec_kit(self.root).to_dict()
        self.assertEqual(
            {"feature_candidate", "interface_candidate", "spec_review_evidence"},
            {item["atlas_role"] for item in result["artifacts"]},
        )
