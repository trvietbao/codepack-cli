"""Tests for scanner and path filtering."""

import unittest
import tempfile
import os
from pathlib import Path
from codepack.scanner import PathFilter, scan_directory


class TestScanner(unittest.TestCase):
    def test_path_filter_ignores_git(self):
        f = PathFilter()
        self.assertTrue(f.should_ignore(".git/config", is_dir=False))
        self.assertTrue(f.should_ignore(".git", is_dir=True))

    def test_path_filter_ignores_pycache(self):
        f = PathFilter()
        self.assertTrue(f.should_ignore("__pycache__/foo.cpython-311.pyc"))
        self.assertTrue(f.should_ignore("src/__pycache__", is_dir=True))

    def test_path_filter_includes(self):
        f = PathFilter(include_patterns=["*.py"])
        self.assertFalse(f.should_ignore("main.py"))
        self.assertTrue(f.should_ignore("readme.md"))

    def test_scan_directory_temp(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "sub").mkdir()
            (tmppath / "file1.py").write_text("print('hello')", encoding="utf-8")
            (tmppath / "sub" / "file2.py").write_text("print('world')", encoding="utf-8")
            (tmppath / "binary.bin").write_bytes(b"\x00\x01\x02")
            (tmppath / ".git").mkdir()
            (tmppath / ".git" / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

            files = scan_directory(tmpdir)
            self.assertIn("file1.py", files)
            self.assertIn("sub/file2.py", files)
            self.assertNotIn("binary.bin", files)
            self.assertNotIn(".git/HEAD", files)


if __name__ == "__main__":
    unittest.main()
