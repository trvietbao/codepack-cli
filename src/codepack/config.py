"""Configuration constants, patterns, and defaults for codepack."""

from typing import Dict, List, Pattern
import re

# Default directories and files to ignore across codebases
DEFAULT_IGNORE_PATTERNS: List[str] = [
    # VCS & IDEs
    ".git/",
    ".svn/",
    ".hg/",
    ".vscode/",
    ".idea/",
    # Python
    "__pycache__/",
    "*.py[cod]",
    ".venv/",
    "venv/",
    "env/",
    "*.egg-info/",
    "build/",
    "dist/",
    ".pytest_cache/",
    ".coverage",
    "htmlcov/",
    # Node.js
    "node_modules/",
    ".npm/",
    ".yarn/",
    # Build & Binaries
    "target/",
    "bin/",
    "obj/",
    "out/",
    "*.exe",
    "*.dll",
    "*.so",
    "*.dylib",
    "*.o",
    "*.obj",
    "*.a",
    # Package lockfiles (often massive and wasteful for LLM context)
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
    # Large media & binary formats
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.webp",
    "*.ico",
    "*.svg",
    "*.pdf",
    "*.zip",
    "*.tar",
    "*.gz",
    "*.7z",
    "*.mp3",
    "*.mp4",
    "*.wav",
    "*.ttf",
    "*.woff",
    "*.woff2",
    # AI cache & graphify
    "graphify-out/",
    ".graphify_analysis.json",
    ".geminiignore",
    # Logs & OS artifacts
    "*.log",
    ".DS_Store",
    "Thumbs.db",
]

# Sensitive credentials & API keys regex patterns
SECRET_PATTERNS: Dict[str, Pattern[str]] = {
    "OpenAI API Key": re.compile(r"\b(sk-[a-zA-Z0-9-]{20,})\b"),
    "GitHub Token": re.compile(r"\b(gh[pousr]_[A-Za-z0-9_]{36,})\b"),
    "AWS Access Key": re.compile(r"\b(AKIA[0-9A-Z]{16})\b"),
    "AWS Secret Key": re.compile(r"(?i)\baws_secret_access_key\s*=\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?"),
    "Generic Private Key": re.compile(r"-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----[^-]+-----END (?:[A-Z ]+)?PRIVATE KEY-----", re.DOTALL),
    "Slack Token": re.compile(r"\b(xox[baprs]-[0-9a-zA-Z-]{10,})\b"),
    "Generic Bearer Token": re.compile(r"(?i)\bBearer\s+([a-zA-Z0-9\-_\.]{24,})\b"),
}

# Mapping common file extensions to markdown syntax highlighting languages
LANGUAGE_EXTENSIONS: Dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "jsx",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".json": "json",
    ".md": "markdown",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".sh": "bash",
    ".bash": "bash",
    ".ps1": "powershell",
    ".sql": "sql",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".xml": "xml",
    ".dockerfile": "dockerfile",
}

# Maximum default file size in bytes (500 KB)
DEFAULT_MAX_FILE_SIZE: int = 500 * 1024
