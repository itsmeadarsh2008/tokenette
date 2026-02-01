# Contributing to Tokenette

Thank you for your interest in contributing to Tokenette! 🎉

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Git

### Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/tokenette.git
   cd tokenette
   ```

2. **Create a virtual environment**
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   uv sync --dev
   ```

4. **Run tests to verify setup**
   ```bash
   pytest
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tokenette

# Run specific test file
pytest tests/test_tokenette.py

# Run specific test
pytest tests/test_tokenette.py::TestRouter::test_complex_task_routing
```

### Code Style

We use `ruff` for linting and formatting:

```bash
# Check code
ruff check .

# Fix issues automatically
ruff check --fix .

# Format code
ruff format .
```

### Type Checking

```bash
# Run mypy
mypy src/tokenette
```

### Running the Server Locally

```bash
# Start the MCP server
tokenette run

# With debug logging
tokenette run --debug

# Test routing
tokenette route "fix a bug in auth.py"

# Analyze a file
tokenette analyze src/tokenette/core/router.py
```

## Making Changes

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new git blame tool
fix: correct token estimation for Python code
docs: update README with new tools
refactor: simplify router selection logic
test: add tests for prompt builder
```

### Pull Request Process

1. **Create a branch** from `main`
2. **Make your changes** with clear commits
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Run the test suite** and fix any failures
6. **Open a PR** with a clear description

### PR Checklist

- [ ] Tests pass (`pytest`)
- [ ] Code is formatted (`ruff format .`)
- [ ] No linting errors (`ruff check .`)
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (for significant changes)

## Project Structure

```
tokenette/
├── src/tokenette/
│   ├── __init__.py       # Package exports
│   ├── cli.py            # CLI commands (typer)
│   ├── config.py         # Pydantic configuration
│   ├── server.py         # FastMCP server & tools
│   ├── core/             # Core components
│   │   ├── router.py     # Task routing engine
│   │   ├── amplifier.py  # Quality amplification
│   │   ├── cache.py      # Multi-layer cache
│   │   ├── optimizer.py  # Optimization pipeline
│   │   └── minifier.py   # Token minification
│   └── tools/            # MCP tool implementations
│       ├── meta.py       # Meta tools
│       ├── file_ops.py   # File operations
│       ├── analysis.py   # Code analysis
│       ├── context7.py   # Context7 integration
│       ├── git_ops.py    # Git operations
│       ├── prompts.py    # Prompt templates
│       ├── tokens.py     # Token/budget tools
│       └── workspace.py  # Workspace analysis
├── tests/
│   └── test_tokenette.py # Test suite
└── pyproject.toml        # Project configuration
```

## Adding New Features

### Adding a New Tool

1. Create the implementation in the appropriate `tools/` module
2. Export from `tools/__init__.py`
3. Register in `server.py` with `@mcp.tool()` decorator
4. Add tests in `tests/test_tokenette.py`
5. Update CHANGELOG.md

### Adding a New Model

1. Add to `MODEL_PROFILES` in `core/router.py`
2. Include: multiplier, quality_score, speed, context_window, strengths, categories, tier, rank
3. Add to `MODEL_COSTS` in `tools/tokens.py`
4. Update tests if needed

### Adding a Prompt Template

1. Add to `TEMPLATES` dict in `tools/prompts.py`
2. Include: name, category, template, description, variables
3. Templates use `{variable}` syntax for substitution

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas

Thank you for contributing! 🚀
