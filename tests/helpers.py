from pathlib import Path
import tempfile
import unittest


def write_record(
    path: Path,
    metadata: dict[str, object],
    body: str = "# Document\n",
) -> Path:
    lines = ["---"]
    for key, value in metadata.items():
        if isinstance(value, list):
            lines.append(f"{key}: [{', '.join(str(item) for item in value)}]")
        else:
            lines.append(f"{key}: {value}")
    lines.extend(["---", body.rstrip("\n"), ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def make_valid_knowledge_base(root: Path) -> Path:
    (root / "03-实施与验收").mkdir(parents=True, exist_ok=True)
    (root / "03-实施与验收" / "CURRENT.md").write_text(
        "# 当前状态\n\n- 当前任务：无可执行开发任务\n",
        encoding="utf-8",
    )
    (root / "03-实施与验收" / "验收矩阵.md").write_text(
        "# 验收矩阵\n\n"
        "| 验收编号 | 对象 | 条件摘要 | 结果 | 证据位置 | 对应版本 |\n"
        "| --- | --- | --- | --- | --- | --- |\n",
        encoding="utf-8",
    )
    for identifier in ("SRC-001", "SRC-002"):
        write_record(
            root / "00-项目总览" / f"{identifier}.md",
            {
                "id": identifier,
                "type": "source",
                "title": identifier,
                "source_type": "user_statement",
                "reference": "test-fixture",
                "last_updated": "2026-08-10",
            },
        )
    return root


class TempDirectoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()
