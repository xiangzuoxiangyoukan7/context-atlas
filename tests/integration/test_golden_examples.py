import json
from pathlib import Path
import unittest

from scripts.project_kb.validator import ValidationConfig, validate


EXAMPLES = ("single-stack", "multi-stack")


def relative_files(root: Path) -> list[str]:
    return sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())


class GoldenExampleTests(unittest.TestCase):
    def test_all_golden_examples_validate(self) -> None:
        config = ValidationConfig(schema_root=Path("schemas"))
        for name in EXAMPLES:
            with self.subTest(name=name):
                self.assertEqual(validate(Path("examples") / name, config), [])

    def test_example_structures_match_snapshot(self) -> None:
        expected = json.loads(
            Path("tests/snapshots/expected-structures.json").read_text(encoding="utf-8")
        )
        actual = {name: relative_files(Path("examples") / name) for name in EXAMPLES}

        self.assertEqual(actual, expected)

    def test_single_and_multi_stack_use_the_same_core_paths(self) -> None:
        single = relative_files(Path("examples") / "single-stack")
        multi = relative_files(Path("examples") / "multi-stack")
        self.assertEqual(single, multi)


if __name__ == "__main__":
    unittest.main()
