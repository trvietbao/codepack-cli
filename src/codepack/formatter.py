"""Output formatters for markdown, XML, and JSON."""

from typing import Dict, List, NamedTuple
import json
from pathlib import Path
from codepack.config import LANGUAGE_EXTENSIONS
from codepack.tokenizer import FileStats, format_bytes, format_tokens


class PackedFile(NamedTuple):
    path: str
    content: str
    stats: FileStats


def detect_language(path: str) -> str:
    """Determine code fence syntax language from file extension."""
    suffix = Path(path).suffix.lower()
    return LANGUAGE_EXTENSIONS.get(suffix, "")


def format_markdown(
    root_name: str,
    tree_text: str,
    files: List[PackedFile],
    total_tokens: int,
    total_bytes: int,
    total_lines: int,
    redactions: Dict[str, int],
) -> str:
    """Format packed codebase into structured, LLM-ready markdown."""
    lines: List[str] = []

    # Header summary
    lines.append(f"# Codebase Context: `{root_name}`")
    lines.append("")
    lines.append(
        f"> **Files**: {len(files)} | **Lines**: {total_lines:,} | "
        f"**Size**: {format_bytes(total_bytes)} | **Tokens**: ~{format_tokens(total_tokens)}"
    )

    if redactions:
        redacted_summary = ", ".join(f"{k}: {v}" for k, v in redactions.items())
        lines.append(f"> 🛡️ **Sanitized Secrets**: {redacted_summary}")

    lines.append("")
    lines.append("## Directory Tree")
    lines.append("```text")
    lines.append(tree_text)
    lines.append("```")
    lines.append("")

    # Files
    for file in files:
        lang = detect_language(file.path)
        fence = "````" if "```" in file.content else "```"
        lines.append(f"## File: `{file.path}`")
        lines.append(f"<!-- {file.stats.formatted_size} | {file.stats.lines} lines | ~{file.stats.formatted_tokens} tokens -->")
        lines.append(f"{fence}{lang}")
        lines.append(file.content)
        lines.append(fence)
        lines.append("")

    return "\n".join(lines)


def format_xml(
    root_name: str,
    tree_text: str,
    files: List[PackedFile],
    total_tokens: int,
    total_bytes: int,
    total_lines: int,
) -> str:
    """Format packed codebase into LLM prompt-optimized XML tags."""
    lines: List[str] = []
    lines.append(f'<codebase root="{root_name}">')
    lines.append("  <summary>")
    lines.append(f"    <files>{len(files)}</files>")
    lines.append(f"    <lines>{total_lines}</lines>")
    lines.append(f"    <bytes>{total_bytes}</bytes>")
    lines.append(f"    <estimated_tokens>{total_tokens}</estimated_tokens>")
    lines.append("  </summary>")
    lines.append("  <directory_tree>")
    lines.append(tree_text)
    lines.append("  </directory_tree>")

    for file in files:
        lines.append(f'  <file path="{file.path}">')
        lines.append(file.content)
        lines.append("  </file>")

    lines.append("</codebase>")
    return "\n".join(lines)


def format_json(
    root_name: str,
    tree_text: str,
    files: List[PackedFile],
    total_tokens: int,
    total_bytes: int,
    total_lines: int,
    redactions: Dict[str, int],
) -> str:
    """Format packed codebase into JSON object for pipeline consumption."""
    data = {
        "root": root_name,
        "summary": {
            "file_count": len(files),
            "total_lines": total_lines,
            "total_bytes": total_bytes,
            "estimated_tokens": total_tokens,
            "redactions": redactions,
        },
        "directory_tree": tree_text,
        "files": [
            {
                "path": f.path,
                "lines": f.stats.lines,
                "bytes": f.stats.size_bytes,
                "tokens": f.stats.tokens,
                "content": f.content,
            }
            for f in files
        ],
    }
    return json.dumps(data, indent=2, ensure_ascii=False)
