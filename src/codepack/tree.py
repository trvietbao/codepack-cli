"""Visual directory tree generation."""

from typing import Dict, List, Optional
import os
from codepack.tokenizer import FileStats


def build_tree_structure(paths: List[str]) -> Dict:
    """Convert a flat list of normalized relative paths into a nested dict."""
    tree: Dict = {}
    for path in sorted(paths):
        parts = path.replace("\\", "/").strip("/").split("/")
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
    return tree


def render_tree(
    root_name: str,
    paths: List[str],
    stats_map: Optional[Dict[str, FileStats]] = None,
    use_unicode: bool = True,
) -> str:
    """Render a visual directory tree for the packed codebase."""
    tree = build_tree_structure(paths)
    lines = [f"{root_name}/"]

    tee = "├── " if use_unicode else "|-- "
    elbow = "└── " if use_unicode else "`-- "
    pipe = "│   " if use_unicode else "|   "
    space = "    "

    def _walk(node: Dict, prefix: str, current_path: str) -> None:
        items = sorted(node.keys())
        for idx, item in enumerate(items):
            is_last = idx == len(items) - 1
            branch = elbow if is_last else tee
            next_prefix = prefix + (space if is_last else pipe)
            child_path = f"{current_path}/{item}" if current_path else item

            child_node = node[item]
            is_dir = bool(child_node)

            label = item + ("/" if is_dir else "")
            if not is_dir and stats_map and child_path in stats_map:
                s = stats_map[child_path]
                label += f" ({s.formatted_size}, ~{s.formatted_tokens} tok)"

            lines.append(f"{prefix}{branch}{label}")
            if is_dir:
                _walk(child_node, next_prefix, child_path)

    _walk(tree, "", "")
    return "\n".join(lines)
