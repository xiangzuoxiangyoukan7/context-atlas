"""验证稳定人员编号、Git 候选发现和隐私保护匹配。"""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess

from tests.helpers import TempDirectoryTestCase


class IdentityTests(TempDirectoryTestCase):
    """验证 Git 信息只用于候选匹配，不自动创建或批准人员身份。"""

    def _people(self, rows: str) -> Path:
        """写入协作人员登记表。"""

        path = self.root / "协作人员.md"
        path.write_text(
            "# 协作人员\n\n"
            "| 人员编号 | 显示名称 | 所属团队 | 状态 | Git 用户名别名 | Git 邮箱摘要 |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            + rows,
            encoding="utf-8",
        )
        return path

    def test_confirmed_email_hash_matches_stable_person(self) -> None:
        """已确认邮箱摘要可以匹配人员，但结果不暴露完整邮箱。"""

        from scripts.project_kb.identity import email_digest, match_git_identity

        digest = email_digest("seven@example.com")
        path = self._people(
            f"| PERSON-001 | Seven | 平台组 | active | seven;nslei | {digest} |\n"
        )

        result = match_git_identity(path, "Another Name", "seven@example.com")

        self.assertEqual("matched", result.status)
        self.assertEqual("PERSON-001", result.person_id)
        self.assertFalse(result.requires_confirmation)
        self.assertNotIn("seven@example.com", repr(result))

    def test_new_git_identity_is_only_unconfirmed_candidate(self) -> None:
        """首次出现的 Git 身份不能自动建立 PERSON 映射。"""

        from scripts.project_kb.identity import match_git_identity

        path = self._people("")

        result = match_git_identity(path, "New Developer", "new@example.com")

        self.assertEqual("candidate", result.status)
        self.assertEqual("PERSON-UNKNOWN", result.person_id)
        self.assertTrue(result.requires_confirmation)
        self.assertEqual(
            hashlib.sha256(b"new@example.com").hexdigest(), result.email_hash
        )

    def test_ambiguous_name_alias_requires_confirmation(self) -> None:
        """用户名同时匹配多人时不得猜测具体人员。"""

        from scripts.project_kb.identity import match_git_identity

        path = self._people(
            "| PERSON-001 | 张三 | A组 | active | shared | — |\n"
            "| PERSON-002 | 李四 | B组 | active | shared | — |\n"
        )

        result = match_git_identity(path, "shared", "shared@example.com")

        self.assertEqual("ambiguous", result.status)
        self.assertEqual("PERSON-UNKNOWN", result.person_id)
        self.assertTrue(result.requires_confirmation)

    def test_local_git_config_is_discovered_without_global_mutation(self) -> None:
        """候选发现读取仓库局部配置，不修改用户全局 Git 信息。"""

        from scripts.project_kb.identity import discover_git_identity

        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "config", "--local", "user.name", "Fixture Developer"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "--local", "user.email", "fixture@example.com"],
            cwd=self.root,
            check=True,
        )

        identity = discover_git_identity(self.root)

        self.assertEqual("Fixture Developer", identity.name)
        self.assertEqual(
            hashlib.sha256(b"fixture@example.com").hexdigest(), identity.email_hash
        )
        self.assertNotIn("fixture@example.com", repr(identity))

    def test_malformed_people_rows_are_reported(self) -> None:
        """重复人员编号和明文邮箱不能被静默接受。"""

        from scripts.project_kb.identity import load_people

        path = self._people(
            "| PERSON-001 | 张三 | A组 | active | zhangsan | zhang@example.com |\n"
            "| PERSON-001 | 张三副本 | A组 | active | zs | — |\n"
        )

        _, issues = load_people(path)
        codes = {issue.code for issue in issues}

        self.assertIn("KB_PERSON_DUPLICATE", codes)
        self.assertIn("KB_PERSON_EMAIL_PRIVACY", codes)
