# Contributing to codepack-cli

Thank you for your interest in contributing to `codepack-cli`! We welcome contributions from the open source community to make codebase packing and context preparation for LLMs faster, safer, and more flexible.

## Development Setup

1. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/trvietbao/codepack-cli.git
   cd codepack-cli
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install the package in editable mode**:
   ```bash
   pip install -e .
   ```

## Running Tests

All unit tests use Python's built-in `unittest` framework with zero external dependencies:

```bash
python -m unittest discover -s tests -v
```

Ensure all tests pass before submitting a pull request.

## Code Standards

- Maintain zero external dependencies for the core library.
- Keep functions concise (< 30 lines) and single-responsibility.
- Add type hints to all function signatures.
- Write unit tests for new features, formatters, or sanitization rules.

## Pull Request Guidelines

1. Create a descriptive feature branch (`git checkout -b feat/my-new-feature`).
2. Commit your changes with clear commit messages.
3. Push to your fork and submit a Pull Request targeting the `main` branch.
4. Verify that all GitHub Actions CI checks pass.
