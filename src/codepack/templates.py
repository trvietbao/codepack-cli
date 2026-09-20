"""Built-in prompt templates for developer workflows with LLMs."""

from typing import Dict, Optional
from pathlib import Path

DEFAULT_TEMPLATES: Dict[str, str] = {
    "review": """You are an experienced software engineer conducting a code review.
Review the attached codebase for:
1. Architecture, modularity, and adherence to clean code principles
2. Potential bugs, unhandled exceptions, and edge cases
3. Security vulnerabilities (input validation, resource leaks)
4. Performance bottlenecks and optimization opportunities

Structure your feedback with clear priorities and actionable code examples.
---
""",
    "audit": """You are a security researcher auditing this repository.
Inspect the following codebase for security weaknesses:
1. Injection risks (SQL, command, path traversal)
2. Authentication and credential management
3. Unsanitized external inputs
4. Insecure defaults or dangerous standard library usage

List all findings with severity (High/Medium/Low) and remediation steps.
---
""",
    "explain": """Explain the architecture and execution flow of this codebase for onboarding engineers.
1. Core entrypoints and module responsibilities
2. Primary data structures and state flow
3. Key dependencies and integration points
4. Non-obvious design decisions or trade-offs
---
""",
    "refactor": """Identify areas of this codebase that would benefit most from refactoring.
Focus on:
1. Reducing coupling and eliminating duplicate logic
2. Improving testability and separating concerns
3. Modernizing legacy patterns to idiomatic idioms

Provide before-and-after code snippets for the top 3 high-impact refactorings.
---
""",
    "test-gen": """Generate unit tests for uncovered code paths in the provided codebase.
For each module:
1. Identify public APIs lacking boundary or failure tests
2. Write tests covering edge cases (empty collections, invalid types, network/IO failures)
3. Follow the Arrange-Act-Assert pattern with clear assertions
---
""",
}


def get_template(name_or_path: Optional[str]) -> Optional[str]:
    """Retrieve template text from built-in name or local file path."""
    if not name_or_path:
        return None

    lower = name_or_path.lower()
    if lower in DEFAULT_TEMPLATES:
        return DEFAULT_TEMPLATES[lower]

    path = Path(name_or_path)
    if path.is_file():
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return None

    return None
