"""Tests for markdown, XML, and JSON formatters."""

import unittest
import json
from codepack.formatter import PackedFile, format_markdown, format_xml, format_json
from codepack.tokenizer import compute_file_stats


class TestFormatters(unittest.TestCase):
    def setUp(self):
        content = "print('hello codex')"
        stats = compute_file_stats("app.py", content)
        self.file = PackedFile(path="app.py", content=content, stats=stats)
        self.files = [self.file]
        self.tree = "root/\n└── app.py"

    def test_markdown_format(self):
        md = format_markdown(
            root_name="demo",
            tree_text=self.tree,
            files=self.files,
            total_tokens=10,
            total_bytes=len(self.file.content),
            total_lines=1,
            redactions={},
        )
        self.assertIn("# Codebase Context: `demo`", md)
        self.assertIn("## File: `app.py`", md)
        self.assertIn("```python", md)
        self.assertIn("print('hello codex')", md)

    def test_xml_format(self):
        xml = format_xml(
            root_name="demo",
            tree_text=self.tree,
            files=self.files,
            total_tokens=10,
            total_bytes=len(self.file.content),
            total_lines=1,
        )
        self.assertIn('<codebase root="demo">', xml)
        self.assertIn('<file path="app.py">', xml)
        self.assertIn("</codebase>", xml)

    def test_json_format(self):
        js = format_json(
            root_name="demo",
            tree_text=self.tree,
            files=self.files,
            total_tokens=10,
            total_bytes=len(self.file.content),
            total_lines=1,
            redactions={"OpenAI API Key": 1},
        )
        data = json.loads(js)
        self.assertEqual(data["root"], "demo")
        self.assertEqual(len(data["files"]), 1)
        self.assertEqual(data["summary"]["redactions"]["OpenAI API Key"], 1)


if __name__ == "__main__":
    unittest.main()
