"""Unit tests for configuration loading."""

import unittest
import tempfile
import json
from pathlib import Path
from codepack.config import load_project_config


class TestProjectConfig(unittest.TestCase):
    def test_load_codepackrc_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = Path(tmpdir) / ".codepackrc"
            cfg_path.write_text(json.dumps({"format": "xml", "sanitize": False}), encoding="utf-8")

            cfg = load_project_config(tmpdir)
            self.assertEqual(cfg.get("format"), "xml")
            self.assertFalse(cfg.get("sanitize"))

    def test_empty_config_when_no_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = load_project_config(tmpdir)
            self.assertEqual(cfg, {})


if __name__ == "__main__":
    unittest.main()
