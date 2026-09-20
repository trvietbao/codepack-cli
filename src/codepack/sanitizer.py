"""Secret detection and sanitization module to prevent sensitive leaks in prompts."""

from typing import Dict, NamedTuple, Pattern
import re
from codepack.config import SECRET_PATTERNS


class SanitizationResult(NamedTuple):
    """Result of sanitizing text, containing cleaned text and detection counts."""
    sanitized_text: str
    redactions: Dict[str, int]

    @property
    def total_redactions(self) -> int:
        return sum(self.redactions.values())


class SecretSanitizer:
    """Detects and masks sensitive credentials, tokens, and private keys."""

    def __init__(self, patterns: Dict[str, Pattern[str]] = None) -> None:
        self.patterns = patterns or SECRET_PATTERNS

    def sanitize(self, text: str) -> SanitizationResult:
        """Scan text and replace sensitive tokens with a safe redaction tag."""
        if not text:
            return SanitizationResult(sanitized_text="", redactions={})

        redaction_counts: Dict[str, int] = {}
        cleaned_text = text

        for name, pattern in self.patterns.items():
            matches = list(pattern.finditer(cleaned_text))
            if not matches:
                continue

            count = len(matches)
            redaction_counts[name] = redaction_counts.get(name, 0) + count

            def _replacer(m: re.Match) -> str:
                # If regex has capture group, mask the capture group
                if m.groups():
                    full_match = m.group(0)
                    captured = m.group(1)
                    tag = f"[REDACTED: {name}]"
                    return full_match.replace(captured, tag)
                return f"[REDACTED: {name}]"

            cleaned_text = pattern.sub(_replacer, cleaned_text)

        return SanitizationResult(sanitized_text=cleaned_text, redactions=redaction_counts)
