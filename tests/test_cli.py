"""Tests for command-line interface execution."""

import unittest
import tempfile
from pathlib import Path
from codepack.cli import main, create_parser


class TestCLI(unittest.TestCase):
    def test_parser_defaults(self):
        parser = create_parser()
        args = parser.parse_args([])
        self.assertEqual(args.path, ".")
        self.assertEqual(args.format, "markdown")
        self.assertFalse(args.no_sanitize)
        self.assertFalse(args.tree_only)

    def test_cli_execution_on_temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "main.py").write_text("print('test')", encoding="utf-8")
            out_file = tmppath / "packed.md"

            code = main([tmpdir, "-o", str(out_file)])
            self.assertEqual(code, 0)
            self.assertTrue(out_file.exists())
            content = out_file.read_text(encoding="utf-8")
            self.assertIn("## File: `main.py`", content)

    def test_cli_tree_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "sample.py").write_text("x = 10", encoding="utf-8")
            code = main([tmpdir, "--tree-only"])
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
