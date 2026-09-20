"""Directory traversal, pattern filtering, and file collection."""

from typing import List, Optional, Set
import fnmatch
import os
from pathlib import Path
from codepack.config import DEFAULT_IGNORE_PATTERNS, DEFAULT_MAX_FILE_SIZE


class PathFilter:
    """Evaluates whether a relative path should be included or ignored."""

    def __init__(
        self,
        ignore_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
    ) -> None:
        self.ignore_patterns = list(ignore_patterns or DEFAULT_IGNORE_PATTERNS)
        self.include_patterns = list(include_patterns or [])

    def should_ignore(self, rel_path: str, is_dir: bool = False) -> bool:
        """Check if path matches any ignore patterns, respecting inclusions."""
        norm_path = rel_path.replace("\\", "/").strip("/")
        if is_dir:
            norm_path += "/"

        # If include patterns are defined, check if file satisfies at least one
        if self.include_patterns and not is_dir:
            if not any(fnmatch.fnmatch(norm_path, pat) or fnmatch.fnmatch(os.path.basename(norm_path), pat) for pat in self.include_patterns):
                return True

        # Check against ignore patterns
        for pattern in self.ignore_patterns:
            clean_pat = pattern.strip()
            if not clean_pat or clean_pat.startswith("#"):
                continue

            if clean_pat.endswith("/"):
                # Directory match
                dir_target = clean_pat.rstrip("/")
                parts = norm_path.strip("/").split("/")
                if any(fnmatch.fnmatch(part, dir_target) for part in parts):
                    return True
            else:
                # File pattern match
                if fnmatch.fnmatch(norm_path, clean_pat) or fnmatch.fnmatch(os.path.basename(norm_path), clean_pat):
                    return True

        return False


def load_gitignore(base_dir: Path) -> List[str]:
    """Parse .gitignore file in directory if present."""
    gitignore_file = base_dir / ".gitignore"
    if not gitignore_file.is_file():
        return []

    try:
        lines = gitignore_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith("#")]
    except OSError:
        return []


def is_binary_file(filepath: Path) -> bool:
    """Detect binary files using git-style null byte inspection."""
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(8192)
            # Null bytes strongly indicate compiled or non-text format
            return b"\x00" in chunk
    except OSError:
        return True


def read_text_safe(filepath: Path) -> str:
    """Read file content with UTF-8, UTF-8-SIG, and Latin-1 fallbacks."""
    raw = filepath.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def scan_directory(
    root_dir: str,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
) -> List[str]:
    """Recursively scan directory and return filtered list of relative paths."""
    base_path = Path(root_dir).resolve()
    if not base_path.exists():
        raise FileNotFoundError(f"Path does not exist: {root_dir}")

    if base_path.is_file():
        return [base_path.name]

    # Combine default ignores, gitignore, and user excludes
    all_ignores = list(DEFAULT_IGNORE_PATTERNS)
    all_ignores.extend(load_gitignore(base_path))
    if exclude_patterns:
        all_ignores.extend(exclude_patterns)

    path_filter = PathFilter(ignore_patterns=all_ignores, include_patterns=include_patterns)
    collected_files: List[str] = []

    for dirpath, dirnames, filenames in os.walk(base_path):
        rel_dir = os.path.relpath(dirpath, base_path)
        if rel_dir == ".":
            rel_dir = ""

        # Filter out ignored directories in-place to prune walk
        dirnames[:] = [d for d in dirnames if not path_filter.should_ignore(os.path.join(rel_dir, d), is_dir=True)]

        for filename in filenames:
            rel_file = os.path.join(rel_dir, filename) if rel_dir else filename
            if path_filter.should_ignore(rel_file, is_dir=False):
                continue

            full_file = Path(dirpath) / filename
            try:
                if full_file.stat().st_size > max_file_size:
                    continue
                if is_binary_file(full_file):
                    continue
            except OSError:
                continue

            # Use forward slashes for cross-platform consistency
            collected_files.append(rel_file.replace("\\", "/"))

    return sorted(collected_files)
