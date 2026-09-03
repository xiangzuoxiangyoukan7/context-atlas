"""验证受管 README 正文契约。"""

from __future__ import annotations

from scripts.project_kb.discovery import discover_records
from scripts.project_kb.readme_contract import validate_readme_contracts
from tests.helpers import TempDirectoryTestCase, materialize_core_template


class ReadmeContractTests(TempDirectoryTestCase):
    """README 不仅要有 front matter，还必须声明目录和查询职责。"""

    def test_stale_readme_body_is_rejected(self) -> None:
        """旧式静态文件清单不能满足当前 README 正文契约。"""

        root = materialize_core_template(self.root, "readme-contract")
        path = root / "01-功能基线/功能/README.md"
        content = path.read_text(encoding="utf-8")
        frontmatter = content.split("---", 2)[1]
        path.write_text(
            f"---{frontmatter}---\n# 功能\n\n## 本目录文件\n\n- 静态列表。\n",
            encoding="utf-8",
        )

        records, discovery_issues = discover_records(root, frozenset())
        issues = validate_readme_contracts(root, records)

        self.assertEqual([], discovery_issues)
        self.assertEqual(
            {
                "KB_README_CONTRACT_REQUIRED",
                "KB_README_QUERY_CONTRACT",
                "KB_README_SCOPE_REQUIRED",
            },
            {issue.code for issue in issues},
        )

    def test_current_template_readmes_satisfy_contract(self) -> None:
        """当前核心模板中的所有正式 README 都应通过契约检查。"""

        root = materialize_core_template(self.root, "readme-contract-current")
        records, discovery_issues = discover_records(root, frozenset())

        self.assertEqual([], discovery_issues)
        self.assertEqual([], validate_readme_contracts(root, records))
