# codepack-cli

<div align="center">

[![CI](https://github.com/trvietbao/codepack-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/trvietbao/codepack-cli/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()
[![OpenAI Codex Ready](https://img.shields.io/badge/OpenAI%20Codex-Ready-412991.svg)]()

**A fast, zero-dependency CLI tool and Python library to pack codebases into structured, LLM-optimized context for OpenAI Codex, ChatGPT, Claude, and local models.**

[Features](#key-features) • [Installation](#installation) • [Quickstart](#quickstart) • [CLI Reference](#cli-reference) • [Python API](#python-api) • [Contributing](#contributing)

</div>

---

## Overview

When working with **OpenAI Codex**, **ChatGPT**, or **Claude**, feeding codebases into prompts often requires:
- Manually excluding bulky directories (`node_modules`, `venv`, `dist`, lockfiles).
- Finding and filtering out binary assets.
- Checking token limits to avoid overflowing context windows.
- Ensuring API keys, credentials, and private keys aren't accidentally exposed.

**`codepack-cli`** solves this in a single command. It scans your repository, applies intelligent ignore rules (including `.gitignore`), automatically redacts sensitive secrets, generates a visual file tree with token estimates, and packages the entire codebase into a clean, model-friendly prompt.

---

## Key Features

- **Zero External Dependencies**: Built entirely on standard Python 3.8+ libraries. Runs anywhere instantly.
- **🛡️ Built-in Secret Sanitization**: Detects and redacts OpenAI API keys (`sk-...`), GitHub PATs (`ghp_...`), AWS credentials, Bearer tokens, and private keys by default before they ever reach an LLM.
- **Prompt Templates**: Prepend battle-tested LLM prompt templates (`--template review`, `audit`, `explain`, `refactor`, `test-gen`, or a custom prompt file) directly before the packed codebase.
- **Project Configuration**: Save project defaults in `.codepackrc`, `codepack.json`, or `pyproject.toml` so team members do not need to repeatedly pass long CLI arguments.
- **Smart Ignore Engine**: Automatically respects `.gitignore`, skipping package locks (`package-lock.json`, `poetry.lock`), binary files, virtual environments, and build artifacts.
- **Accurate Token Estimation**: Fast BPE-calibrated token estimator designed for OpenAI GPT-4 / Codex context windows.
- **Visual Directory Tree**: Generates an ASCII/Unicode hierarchy tree showing file sizes and estimated token consumption per module.
- **Multiple Output Formats**: Export to Markdown (with language-specific code fences), prompt-optimized XML tags, or structured JSON.
- **Direct Clipboard Copying**: Use `-c` or `--copy` to copy directly to your OS clipboard (macOS, Linux, Windows).
- **PEP 561 Typed**: Includes `py.typed` marker with comprehensive type annotations for seamless editor autocomplete and mypy verification.

---

## Installation

### From Source / Git
```bash
git clone https://github.com/trvietbao/codepack-cli.git
cd codepack-cli
pip install -e .
```

### Direct Pip Install
```bash
pip install git+https://github.com/trvietbao/codepack-cli.git
```

---

## Quickstart

### 1. Pack current directory to Markdown
```bash
codepack . -o prompt.md
```

### 2. Pack with an LLM Code Review Template and copy to clipboard
```bash
codepack . --template review --copy
```

### 3. Inspect directory tree and token breakdown
```bash
codepack . --tree-only
```
Output:
```text
my-project/
├── src/
│   └── app.py (2.4 KB, ~620 tok)
├── tests/
│   └── test_app.py (1.1 KB, ~280 tok)
└── README.md (1.8 KB, ~450 tok)

Total: 3 files, ~1.4k tokens
```

### 4. Display file-by-file metrics table
```bash
codepack . --stats
```

### 5. Pack specific patterns
```bash
codepack . --include "*.py,*.ts" --exclude "tests/*" -o prompt.md
```

---

## Prompt Templates

`codepack-cli` includes built-in developer prompt templates designed for OpenAI Codex and GPT-4 workflows:

| Template | Flag | Description |
| :--- | :--- | :--- |
| **Code Review** | `-t review` | Modular architecture, potential bugs, security vulnerabilities, and code quality suggestions. |
| **Security Audit** | `-t audit` | Vulnerability assessment for injection, auth, input sanitization, and insecure defaults. |
| **Codebase Explanation** | `-t explain` | Entrypoints, state flow, dependencies, and onboarding walkthrough. |
| **Refactoring** | `-t refactor` | Targeted recommendations to reduce coupling, eliminate duplication, and modernize patterns. |
| **Test Generation** | `-t test-gen` | Unit tests for uncovered branches and edge cases using AAA pattern. |
| **Custom Template** | `-t ./prompt.txt` | Load instructions from any local file. |

---

## Configuration File

You can store recurring settings in `.codepackrc` or `codepack.json` at your project root:

```json
{
  "format": "markdown",
  "sanitize": true,
  "max_size_kb": 300,
  "template": "review",
  "exclude": ["tests/fixtures/*", "docs/*"]
}
```

Or inside `pyproject.toml`:

```toml
[tool.codepack]
format = "markdown"
sanitize = true
template = "review"
```

---

## CLI Reference

```text
usage: codepack [path] [-o OUTPUT] [-f {markdown,xml,json}] [-t TEMPLATE]
                [--tree-only] [--stats] [--no-sanitize] [--include INCLUDE]
                [--exclude EXCLUDE] [--max-size MAX_SIZE] [-c] [-v]

Pack your codebase into clean, LLM-optimized context for OpenAI Codex & Claude.

positional arguments:
  path                  Target directory or file (default: current directory)

options:
  -o, --output OUTPUT   Save packed context to specified file path
  -f, --format FORMAT   Output format: markdown, xml, json (default: markdown)
  -t, --template TEXT   Prepend LLM prompt template (review, audit, explain, refactor, test-gen, or file)
  --tree-only           Print only directory tree structure and token summary
  --stats               Display file-by-file size, line, and token statistics
  --no-sanitize         Disable automatic credential & secret redaction
  --include INCLUDE     Comma-separated patterns to include (e.g. '*.py,*.ts')
  --exclude EXCLUDE     Comma-separated patterns to exclude (e.g. 'tests/*')
  --max-size MAX_SIZE   Maximum file size in KB to include (default: 500 KB)
  -c, --copy            Copy packed content directly to clipboard
  -v, --version         Show program's version number and exit
```

---

## Python API

You can import `codepack` directly into your Python applications or LLM agents:

```python
from codepack import pack_codebase

# Pack current project into Markdown
result = pack_codebase(".", output_format="markdown", sanitize=True)

print(f"Packed {result.file_count} files.")
print(f"Total tokens: ~{result.total_tokens}")
print(f"Redactions made: {result.redactions}")

# Access full generated prompt
prompt_text = result.content
```

Using the `CodePacker` class for custom configurations:

```python
from codepack import CodePacker

packer = CodePacker(
    sanitize=True,
    max_file_size=200 * 1024,  # 200 KB
    include_patterns=["*.py"],
    exclude_patterns=["tests/*"]
)

result = packer.pack("./src", output_format="xml")
print(result.content)
```

---

## Output Example (Markdown)

```markdown
# Codebase Context: `my-project`

> **Files**: 3 | **Lines**: 142 | **Size**: 5.3 KB | **Tokens**: ~1.4k
> 🛡️ **Sanitized Secrets**: OpenAI API Key: 1

## Directory Tree
```text
my-project/
├── src/
│   └── app.py (2.4 KB, ~620 tok)
└── README.md (1.8 KB, ~450 tok)
```

## File: `src/app.py`
```python
# Application entrypoint
def main():
    api_key = "[REDACTED: OpenAI API Key]"
    ...
```
```

---

## Contributing

Contributions, bug reports, and feature requests are welcome! Check out [CONTRIBUTING.md](CONTRIBUTING.md) for setup and guidelines.

1. Fork the repo.
2. Create your feature branch (`git checkout -b feat/my-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feat/my-feature`).
5. Open a Pull Request.

---

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
