"""Unit tests for codepack."""

import sys
from pathlib import Path

# Ensure src is discoverable in test runs
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
