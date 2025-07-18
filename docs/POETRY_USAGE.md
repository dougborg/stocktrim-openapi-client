# Poetry Usage Guide

This project uses Poetry for dependency management and packaging. Here are the essential
commands for development workflow.

## Installation and Setup

### Initial Setup

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Clone the repository
git clone <repository-url>
cd stocktrim-openapi-client

# Install all dependencies
poetry install

# Activate virtual environment
poetry shell
# Or use: source .venv/bin/activate.fish (for fish shell)
```

### Environment Configuration

Poetry automatically creates a virtual environment. Configure it:

```bash
# Show virtual environment info
poetry env info

# Show virtual environment path
poetry env info --path

# Use specific Python version
poetry env use python3.11  # or 3.12, 3.13
```

## Dependency Management

### Adding Dependencies

```bash
# Add runtime dependency
poetry add httpx
poetry add "httpx>=0.24.0"

# Add development dependency
poetry add --group dev pytest
poetry add --group dev "mypy>=1.0"

# Add optional dependencies
poetry add --optional requests
```

### Removing Dependencies

```bash
# Remove runtime dependency
poetry remove httpx

# Remove development dependency
poetry remove --group dev pytest
```

### Updating Dependencies

```bash
# Update all dependencies
poetry update

# Update specific dependency
poetry update httpx

# Show outdated dependencies
poetry show --outdated
```

### Dependency Information

```bash
# List all dependencies
poetry show

# Show dependency tree
poetry show --tree

# Show specific dependency details
poetry show httpx
```

## Poethepoet Tasks

This project uses poethepoet (poe) for task automation. All tasks are defined in
`pyproject.toml`.

### Core Development Tasks

```bash
# Format all code (Python + Markdown)
poetry run poe format

# Check formatting without making changes
poetry run poe format-check

# Run type checking with mypy
poetry run poe lint

# Run all tests
poetry run poe test

# Full quality check (format-check + lint + test)
poetry run poe check

# Auto-fix formatting and linting issues
poetry run poe fix

# Complete CI pipeline
poetry run poe ci
```

### Specialized Tasks

```bash
# Python-only formatting
poetry run poe format-python

# Markdown-only formatting
poetry run poe format-markdown

# Different test categories
poetry run poe test-unit
poetry run poe test-integration
poetry run poe test-coverage

# Regenerate OpenAPI client
poetry run poe regenerate-client

# Check generated client AST validity
poetry run poe check-generated-ast
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks (required for development)
poetry run poe pre-commit-install

# Run pre-commit on all files
poetry run poe pre-commit-run

# Update pre-commit hook versions
poetry run poe pre-commit-update
```

### Available Tasks

```bash
# Show all available tasks
poetry run poe --help

# Or show with descriptions
poetry run poe help
```

## Virtual Environment Management

### Activation

```bash
# Option 1: Poetry shell (recommended)
poetry shell

# Option 2: Source activation script
# For bash/zsh:
source .venv/bin/activate

# For fish shell:
source .venv/bin/activate.fish

# Option 3: Run commands with Poetry
poetry run python script.py
poetry run pytest
```

### Deactivation

```bash
# Exit poetry shell
exit

# Or deactivate virtual environment
deactivate
```

### Environment Information

```bash
# Show environment details
poetry env info

# List all Poetry environments
poetry env list

# Remove current environment
poetry env remove python
```

## Building and Publishing

### Building

```bash
# Build distribution packages
poetry build

# Build only wheel
poetry build --format wheel

# Build only sdist
poetry build --format sdist
```

### Version Management

```bash
# Show current version
poetry version

# Bump version
poetry version patch    # 1.0.0 -> 1.0.1
poetry version minor    # 1.0.0 -> 1.1.0
poetry version major    # 1.0.0 -> 2.0.0

# Set specific version
poetry version 1.2.3
```

### Publishing

```bash
# Configure PyPI credentials (one time)
poetry config pypi-token.pypi <your-token>

# Publish to PyPI
poetry publish

# Build and publish in one step
poetry publish --build

# Publish to test PyPI
poetry publish --repository testpypi
```

## Configuration

### Poetry Configuration

```bash
# Show current configuration
poetry config --list

# Set configuration values
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true
poetry config repositories.testpypi https://test.pypi.org/legacy/
```

### pyproject.toml Structure

The project follows PEP 621 standards with configuration in `pyproject.toml`:

```toml
[project]
name = "stocktrim-openapi-client"
version = "0.1.0"
description = "StockTrim Inventory Management API client"
# ... project metadata

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "mypy>=1.0",
    # ... development dependencies
]

[tool.poetry]
packages = [
    { include = "stocktrim_public_api_client" }
]

[tool.poe.tasks]
format = ["format-python", "format-markdown"]
# ... task definitions
```

## Troubleshooting

### Common Issues

#### Poetry Not Found

```bash
# Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or reinstall Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

#### Virtual Environment Issues

```bash
# Remove and recreate environment
poetry env remove python
poetry install

# Use specific Python version
poetry env use /usr/bin/python3.11
```

#### Dependency Conflicts

```bash
# Clear Poetry cache
poetry cache clear pypi --all

# Force reinstall
poetry install --no-cache
```

#### Lock File Issues

```bash
# Update lock file
poetry lock

# Force lock file update
poetry lock --no-update
```

### Performance Tips

```bash
# Install without development dependencies (production)
poetry install --only main

# Skip building packages that have wheels
poetry install --no-compile

# Parallel installation
poetry config installer.parallel true
```

## Integration with IDEs

### VS Code

1. Install Python extension
1. Set Python interpreter to Poetry venv:
   - `Cmd+Shift+P` → "Python: Select Interpreter"
   - Choose `.venv/bin/python`
1. Configure tasks in `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "poetry-check",
            "type": "shell",
            "command": "poetry",
            "args": ["run", "poe", "check"],
            "group": "test"
        }
    ]
}
```

### PyCharm

1. Go to Settings → Project → Python Interpreter
1. Add interpreter → Poetry Environment
1. Select existing environment: `.venv/bin/python`

## Best Practices

### Development Workflow

```bash
# 1. Start development session
poetry shell

# 2. Make changes to code

# 3. Run quality checks
poetry run poe check

# 4. Run tests
poetry run poe test

# 5. Format code (if needed)
poetry run poe format

# 6. Commit changes (pre-commit hooks run automatically)
git add .
git commit -m "feat: add new feature"
```

### Dependency Guidelines

- **Pin major versions**: Use `"^1.0"` to allow minor updates
- **Group dependencies**: Use `--group dev` for development tools
- **Regular updates**: Run `poetry update` periodically
- **Lock file**: Always commit `poetry.lock`

### Environment Management

- **Use Poetry shell**: Preferred over manual activation
- **Project isolation**: Each project gets its own environment
- **Clean environments**: Remove unused environments periodically

This guide covers all essential Poetry operations for effective development workflow
with the StockTrim OpenAPI client.
