"""Unit tests for developer prompt templates."""

import unittest
import tempfile
from pathlib import Path
from codepack.templates import get_template, DEFAULT_TEMPLATES
from codepack import CodePacker


class TestTemplates(unittest.TestCase):
    def test_default_templates_exist(self):
        for name in ("review", "audit", "explain", "refactor", "test-gen"):
            tmpl = get_template(name)
            self.assertIsNotNone(tmpl)
            self.assertGreater(len(tmpl), 20)

    def test_custom_file_template(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("Custom instructions for Codex\n---\n")
            filepath = f.name

        try:
            tmpl = get_template(filepath)
            self.assertEqual(tmpl, "Custom instructions for Codex\n---\n")
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_packer_prepends_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.py").write_text("x = 1", encoding="utf-8")
            packer = CodePacker(template="review")
            res = packer.pack(tmpdir)
            self.assertIn("code review", res.content.lower())
            self.assertIn("## File: `app.py`", res.content)


if __name__ == "__main__":
    unittest.main()
