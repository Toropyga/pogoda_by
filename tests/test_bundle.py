"""Validate packaging and the translated config-flow/entity contracts."""

import ast
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components/pogoda_by"


def keys(value, prefix=""):
    if not isinstance(value, dict):
        return {prefix}
    return set().union(*(keys(child, f"{prefix}.{key}") for key, child in value.items()))


class BundleTests(unittest.TestCase):
    def test_manifest(self):
        manifest = json.loads((COMPONENT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["domain"], "pogoda_by")
        self.assertTrue(manifest["config_flow"])
        self.assertEqual(manifest["iot_class"], "cloud_polling")
        self.assertTrue(manifest["version"])
        self.assertEqual(manifest["requirements"], [])

    def test_all_python_syntax(self):
        for path in ROOT.rglob("*.py"):
            with self.subTest(file=str(path.relative_to(ROOT))):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_translations_have_matching_keys(self):
        source = json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))
        for language in ("en", "ru", "pl"):
            translated = json.loads((COMPONENT / f"translations/{language}.json").read_text(encoding="utf-8"))
            self.assertEqual(keys(source), keys(translated))
            self.assertIn("{country}", translated["config"]["step"]["station"]["description"])
        self.assertEqual(source, json.loads((COMPONENT / "translations/en.json").read_text(encoding="utf-8")))

    def test_sensor_descriptions_have_translations(self):
        tree = ast.parse((COMPONENT / "sensor.py").read_text(encoding="utf-8"))
        descriptions = {
            keyword.value.value
            for node in ast.walk(tree) if isinstance(node, ast.Call)
            for keyword in node.keywords
            if keyword.arg == "translation_key" and isinstance(keyword.value, ast.Constant)
        }
        source = json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))
        self.assertEqual(descriptions, set(source["entity"]["sensor"]))


if __name__ == "__main__":
    unittest.main()
