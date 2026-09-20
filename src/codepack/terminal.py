"""Terminal color and formatting utilities honoring NO_COLOR standards."""

import os
import sys

_NO_COLOR = bool(os.environ.get("NO_COLOR"))
_IS_DUMB = os.environ.get("TERM", "").lower() == "dumb"


def can_color(stream=None) -> bool:
    """Check if output stream supports ANSI colors."""
    if _NO_COLOR or _IS_DUMB:
        return False
    target = stream or sys.stdout
    return hasattr(target, "isatty") and target.isatty()


def color(text: str, code: str, stream=None) -> str:
    """Wrap text in ANSI color sequence if supported."""
    if not can_color(stream):
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(text: str) -> str:
    return color(text, "1")


def dim(text: str) -> str:
    return color(text, "2")


def green(text: str) -> str:
    return color(text, "32")


def yellow(text: str) -> str:
    return color(text, "33")


def cyan(text: str) -> str:
    return color(text, "36")
