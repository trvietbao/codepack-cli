"""Token estimation and codebase statistical calculation."""

from typing import NamedTuple
import re


class FileStats(NamedTuple):
    """Statistical metrics for a single file."""
    path: str
    size_bytes: int
    lines: int
    tokens: int

    @property
    def formatted_size(self) -> str:
        return format_bytes(self.size_bytes)

    @property
    def formatted_tokens(self) -> str:
        return format_tokens(self.tokens)


# Fast regex pattern approximating GPT BPE tokenization rules for code & text
_TOKEN_PATTERN = re.compile(
    r"""(?x)
    [a-zA-Z]+
    |\d+
    |[^\s\w]+
    |\n
    |\ {2,4}
    |\s
    """
)


def estimate_tokens(text: str) -> int:
    """Accurately estimate token count for text in OpenAI GPT / Codex models.

    Uses a calibrated subword regex pattern that accounts for identifiers,
    numbers, punctuation, code indentation spaces, and newlines without
    requiring heavy external dependencies.
    """
    if not text:
        return 0
    # Count token fragments
    tokens = len(_TOKEN_PATTERN.findall(text))
    return max(1, tokens)


def compute_file_stats(path: str, content: str) -> FileStats:
    """Calculate lines, bytes, and estimated tokens for a file."""
    encoded = content.encode("utf-8", errors="replace")
    size_bytes = len(encoded)
    lines = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
    tokens = estimate_tokens(content)
    return FileStats(path=path, size_bytes=size_bytes, lines=lines, tokens=tokens)


def format_bytes(num_bytes: int) -> str:
    """Format bytes into human-readable representation."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    else:
        return f"{num_bytes / (1024 * 1024):.2f} MB"


def format_tokens(num_tokens: int) -> str:
    """Format token count into readable format (e.g. 1.5k, 45k)."""
    if num_tokens < 1000:
        return f"{num_tokens}"
    elif num_tokens < 1000000:
        return f"{num_tokens / 1000:.1f}k"
    else:
        return f"{num_tokens / 1000000:.2f}M"
