"""codepack: LLM-optimized codebase context packing library and CLI."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import os

from codepack.config import DEFAULT_MAX_FILE_SIZE
from codepack.scanner import scan_directory, read_text_safe
from codepack.sanitizer import SecretSanitizer
from codepack.tokenizer import FileStats, compute_file_stats, estimate_tokens
from codepack.tree import render_tree
from codepack.formatter import PackedFile, format_markdown, format_xml, format_json
from codepack.templates import get_template

__version__ = "0.1.0"
__all__ = ["CodePacker", "PackResult", "pack_codebase", "__version__"]


@dataclass
class PackResult:
    """Result of packing a codebase."""
    content: str
    directory_tree: str
    file_count: int
    total_lines: int
    total_bytes: int
    total_tokens: int
    redactions: Dict[str, int]
    files: List[PackedFile]


class CodePacker:
    """Core engine to scan, sanitize, and pack codebases into LLM prompts."""

    def __init__(
        self,
        sanitize: bool = True,
        max_file_size: int = DEFAULT_MAX_FILE_SIZE,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        template: Optional[str] = None,
    ) -> None:
        self.sanitize = sanitize
        self.max_file_size = max_file_size
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.template_text = get_template(template)
        self.sanitizer = SecretSanitizer() if sanitize else None

    def pack(self, target_path: str, output_format: str = "markdown") -> PackResult:
        """Scan target path and pack files into the selected format."""
        path_obj = Path(target_path).resolve()
        root_name = path_obj.name or "root"

        rel_paths = scan_directory(
            root_dir=str(path_obj),
            include_patterns=self.include_patterns,
            exclude_patterns=self.exclude_patterns,
            max_file_size=self.max_file_size,
        )

        packed_files: List[PackedFile] = []
        stats_map: Dict[str, FileStats] = {}
        all_redactions: Dict[str, int] = {}
        total_bytes = 0
        total_lines = 0

        for rel in rel_paths:
            full_path = path_obj / rel if path_obj.is_dir() else path_obj
            try:
                raw_text = read_text_safe(full_path)
            except OSError:
                continue

            if self.sanitizer:
                san_res = self.sanitizer.sanitize(raw_text)
                cleaned_text = san_res.sanitized_text
                for k, v in san_res.redactions.items():
                    all_redactions[k] = all_redactions.get(k, 0) + v
            else:
                cleaned_text = raw_text

            file_stat = compute_file_stats(rel, cleaned_text)
            stats_map[rel] = file_stat
            total_bytes += file_stat.size_bytes
            total_lines += file_stat.lines
            packed_files.append(PackedFile(path=rel, content=cleaned_text, stats=file_stat))

        tree_str = render_tree(root_name, rel_paths, stats_map=stats_map)
        total_tokens = sum(f.stats.tokens for f in packed_files) + estimate_tokens(tree_str)

        fmt = output_format.lower()
        if fmt == "xml":
            content = format_xml(root_name, tree_str, packed_files, total_tokens, total_bytes, total_lines)
        elif fmt == "json":
            content = format_json(root_name, tree_str, packed_files, total_tokens, total_bytes, total_lines, all_redactions)
        else:
            content = format_markdown(root_name, tree_str, packed_files, total_tokens, total_bytes, total_lines, all_redactions)

        # Prepend developer prompt template if configured
        if self.template_text:
            content = f"{self.template_text.strip()}\n\n{content}"
            total_tokens += estimate_tokens(self.template_text)

        return PackResult(
            content=content,
            directory_tree=tree_str,
            file_count=len(packed_files),
            total_lines=total_lines,
            total_bytes=total_bytes,
            total_tokens=total_tokens,
            redactions=all_redactions,
            files=packed_files,
        )


def pack_codebase(
    target_path: str = ".",
    output_format: str = "markdown",
    sanitize: bool = True,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    template: Optional[str] = None,
) -> PackResult:
    """Convenience function to pack a codebase into an LLM context bundle."""
    packer = CodePacker(
        sanitize=sanitize,
        max_file_size=max_file_size,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        template=template,
    )
    return packer.pack(target_path, output_format=output_format)
