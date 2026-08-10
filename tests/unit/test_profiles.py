import json
from pathlib import Path

from scripts.project_kb.validator import ValidationConfig, validate
from tests.helpers import TempDirectoryTestCase, materialize_core_template


PROFILE_ADDITIONS = {
    "java.v1": Path("00-项目总览/技术栈-Java.md"),
    "python.v1": Path("00-项目总览/技术栈-Python.md"),
}


class ProfileTests(TempDirectoryTestCase):
    def test_profiles_are_optional_and_composable(self) -> None:
        combinations = ((), ("java.v1",), ("python.v1",), ("java.v1", "python.v1"))
        for index, profiles in enumerate(combinations):
            with self.subTest(profiles=profiles):
                root = materialize_core_template(self.root / str(index), "example", profiles)
                issues = validate(root, ValidationConfig(schema_root=Path("schemas")))
                manifest = (root / "knowledge-base.yaml").read_text(encoding="utf-8")

                self.assertEqual(issues, [])
                for profile_id in profiles:
                    self.assertTrue((root / PROFILE_ADDITIONS[profile_id]).exists())
                    self.assertTrue((root / ".project-kb/profiles" / f"{profile_id}.json").exists())
                    self.assertIn(profile_id, manifest)

    def test_supported_descriptors_are_schema_valid_and_additive(self) -> None:
        from scripts.project_kb.profiles import validate_profile_descriptor

        for path in (Path("profiles/java/profile.json"), Path("profiles/python/profile.json")):
            with self.subTest(path=path):
                self.assertEqual(validate_profile_descriptor(path, Path("schemas")), [])

    def test_profile_cannot_override_core_contracts(self) -> None:
        from scripts.project_kb.profiles import validate_profile_descriptor

        base = {
            "profile_id": "invalid.v1",
            "title": "Invalid",
            "project_types": ["example"],
            "added_fields": ["runtime_detail"],
            "added_templates": ["00-项目总览/技术栈-Invalid.md"],
            "added_requests": ["Confirm runtime"],
            "added_acceptance_checks": ["Runtime is reproducible"],
            "exclusions": [],
        }
        overrides = {
            "core_statuses": ["custom"],
            "authority_paths": ["custom/CURRENT.md"],
            "approval_rules": ["AI may approve"],
            "acceptance_results": ["failed"],
            "added_fields": ["status"],
        }
        for field, value in overrides.items():
            with self.subTest(field=field):
                descriptor = dict(base)
                descriptor[field] = value
                path = self.root / f"{field}.json"
                path.write_text(json.dumps(descriptor), encoding="utf-8")

                codes = {
                    issue.code for issue in validate_profile_descriptor(path, Path("schemas"))
                }

                self.assertIn("KB_PROFILE_OVERRIDE", codes)


if __name__ == "__main__":
    import unittest

    unittest.main()
