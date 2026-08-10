from pathlib import Path
import re
from urllib.parse import unquote

from scripts.project_kb.links import LINK_PATTERN
from scripts.project_kb.template_contract import TEMPLATE_MARKERS, required_template_paths
from scripts.project_kb.validator import ValidationConfig, validate
from tests.helpers import TempDirectoryTestCase, materialize_core_template


class CoreTemplateTests(TempDirectoryTestCase):
    def test_core_template_contains_every_required_knowledge_type(self) -> None:
        root = Path("templates/core/doc-project")
        missing = [path for path in required_template_paths() if not (root / path).exists()]
        markers = {
            marker
            for path in root.rglob("*")
            if path.is_file()
            for marker in re.findall(r"{{[A-Z][A-Z0-9_]*}}", path.read_text(encoding="utf-8"))
        }

        self.assertEqual(missing, [])
        self.assertEqual(markers, TEMPLATE_MARKERS)

    def test_materialized_template_is_self_contained_and_valid(self) -> None:
        root = materialize_core_template(self.root, "example")
        unresolved: list[tuple[Path, str]] = []
        escaped: list[tuple[Path, str]] = []
        broken: list[tuple[Path, str]] = []

        for path in root.rglob("*"):
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8")
            unresolved.extend((path, marker) for marker in re.findall(r"{{[A-Z][A-Z0-9_]*}}", content))
            if path.suffix != ".md":
                continue
            for target in LINK_PATTERN.findall(content):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                candidate = (path.parent / unquote(target.split("#", 1)[0])).resolve()
                if not candidate.is_relative_to(root.resolve()):
                    escaped.append((path, target))
                elif not candidate.exists():
                    broken.append((path, target))

        self.assertEqual(unresolved, [])
        self.assertEqual(escaped, [])
        self.assertEqual(broken, [])
        self.assertEqual(
            validate(root, ValidationConfig(schema_root=Path("schemas"))),
            [],
        )


if __name__ == "__main__":
    import unittest

    unittest.main()
