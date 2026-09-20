"""Command-line interface for codepack."""

import argparse
import sys
import subprocess
from pathlib import Path
from typing import List, Optional

from codepack import __version__, CodePacker
from codepack.config import DEFAULT_MAX_FILE_SIZE, load_project_config
from codepack.tokenizer import format_bytes, format_tokens
from codepack.terminal import bold, cyan, green, yellow, dim

# Ensure stdout and stderr handle unicode characters across all platforms
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard using native OS utilities without dependencies."""
    try:
        if sys.platform == "win32":
            proc = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
            proc.communicate(text.encode("utf-16le"))
            return proc.returncode == 0
        elif sys.platform == "darwin":
            proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            proc.communicate(text.encode("utf-8"))
            return proc.returncode == 0
        else:
            proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
            proc.communicate(text.encode("utf-8"))
            return proc.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def parse_comma_separated(value: Optional[str]) -> List[str]:
    """Parse comma-separated pattern list."""
    if not value:
        return []
    return [p.strip() for p in value.split(",") if p.strip()]


def print_stats_table(result) -> None:
    """Print an aligned terminal table showing file metrics."""
    header = f"{bold('File Path'):<59} {bold('Size'):<19} {bold('Lines'):<17} {bold('Tokens'):<19}"
    raw_header = f"{'File Path':<50} {'Size':<10} {'Lines':<8} {'Tokens':<10}"
    separator = dim("-" * len(raw_header))
    print(header)
    print(separator)
    for f in result.files:
        p = f.path if len(f.path) <= 48 else "..." + f.path[-45:]
        print(f"{p:<50} {f.stats.formatted_size:<10} {f.stats.lines:<8} {cyan(f.stats.formatted_tokens):<19}")
    print(separator)
    print(
        f"{bold('TOTAL (' + str(result.file_count) + ' files)'):<59} "
        f"{format_bytes(result.total_bytes):<10} "
        f"{result.total_lines:<8} "
        f"{green(format_tokens(result.total_tokens)):<19}"
    )


def create_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="codepack",
        description="Pack your codebase into clean, LLM-optimized context for OpenAI Codex & Claude.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Target directory or file (default: current directory)")
    parser.add_argument("-o", "--output", help="Save packed context to specified file path")
    parser.add_argument("-f", "--format", choices=["markdown", "xml", "json"], default="markdown", help="Output format (default: markdown)")
    parser.add_argument("-t", "--template", help="Prepend LLM prompt template (review, audit, explain, refactor, test-gen, or file path)")
    parser.add_argument("--tree-only", action="store_true", help="Print only directory tree structure and token summary")
    parser.add_argument("--stats", action="store_true", help="Display file-by-file size, line, and token statistics")
    parser.add_argument("--no-sanitize", action="store_true", help="Disable automatic credential & secret redaction")
    parser.add_argument("--include", help="Comma-separated patterns to include (e.g. '*.py,*.ts')")
    parser.add_argument("--exclude", help="Comma-separated patterns to exclude (e.g. 'tests/*')")
    parser.add_argument("--max-size", type=int, default=500, help="Maximum file size in KB to include (default: 500 KB)")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy packed content directly to clipboard")
    parser.add_argument("-v", "--version", action="version", version=f"codepack {__version__}")
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    cfg = load_project_config(parsed_args.path)

    # CLI flags take precedence over config file defaults
    fmt = parsed_args.format if parsed_args.format != "markdown" or "format" not in cfg else cfg["format"]
    template = parsed_args.template or cfg.get("template")
    max_size_kb = parsed_args.max_size if parsed_args.max_size != 500 or "max_size_kb" not in cfg else cfg["max_size_kb"]
    sanitize = not parsed_args.no_sanitize if not parsed_args.no_sanitize else cfg.get("sanitize", True)

    inc = parse_comma_separated(parsed_args.include) or cfg.get("include", [])
    exc = parse_comma_separated(parsed_args.exclude) or cfg.get("exclude", [])

    packer = CodePacker(
        sanitize=sanitize,
        max_file_size=max_size_kb * 1024,
        include_patterns=inc,
        exclude_patterns=exc,
        template=template,
    )

    try:
        result = packer.pack(parsed_args.path, output_format=fmt)
    except Exception as e:
        print(f"Error packing codebase: {e}", file=sys.stderr)
        return 1

    if parsed_args.stats:
        print_stats_table(result)
        return 0

    if parsed_args.tree_only:
        print(result.directory_tree)
        print(f"\n{bold('Total')}: {result.file_count} files, ~{green(format_tokens(result.total_tokens))} tokens")
        return 0

    if parsed_args.copy:
        if copy_to_clipboard(result.content):
            print(green(f"Copied {result.file_count} files (~{format_tokens(result.total_tokens)} tokens) to clipboard."))
        else:
            print("Failed to copy to clipboard.", file=sys.stderr)

    if parsed_args.output:
        out_path = Path(parsed_args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result.content, encoding="utf-8")
        print(green(f"Packed {result.file_count} files into {out_path} (~{format_tokens(result.total_tokens)} tokens)"))
    elif not parsed_args.copy:
        sys.stdout.write(result.content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
