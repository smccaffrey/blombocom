# Blombo

A semantic layer middleware for AI/LLM applications that connects various data sources and exposes them as context to LLMs.

## Features

- Modular plugin-like connectors for various data sources
- Unified context engine for structuring and enriching data
- Pluggable interface for multiple LLM providers
- FastAPI server for HTTP endpoints
- Dependency injection and async support
- Strong testing suite with pytest and httpx
- Type safety with mypy and pydantic
- CI-ready with linting (ruff) and formatting (black)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/blombo.git
cd blombo
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Development

The project uses Poetry for dependency management and includes several development tools:

- Format code:
```bash
make format
```

- Run linting:
```bash
make lint
```

- Run tests:
```bash
make test
```

- Start the development server:
```bash
make run
```

## Project Structure

```
blombo/
├── src/
│   └── blombo/
│       ├── api/           # FastAPI server and endpoints
│       ├── connectors/    # Data source connectors
│       ├── core/          # Core functionality
│       └── llm_providers/ # LLM provider implementations
├── tests/                 # Test suite
├── .github/              # GitHub Actions workflows
├── pyproject.toml        # Poetry configuration
└── Makefile             # Development tasks
```

## Connectors

Currently supported connectors:
- Local Markdown files

## LLM Providers

Currently supported providers:
- OpenAI (GPT-4, GPT-3.5, embeddings)

## API Endpoints

- `POST /generate` - Generate text with context
- `GET /health` - Health check endpoint

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Development Setup

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and consistency. The hooks will run automatically on each commit, checking and formatting your code according to the project's standards.

#### Setup

1. Install pre-commit:
   ```bash
   poetry install
   ```

2. Install the pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```

3. (Optional) Run against all files:
   ```bash
   poetry run pre-commit run --all-files
   ```

#### Hooks

The following hooks are configured:

- **pre-commit-hooks**: Basic file checks (trailing whitespace, YAML validity, etc.)
- **black**: Code formatting
- **isort**: Import sorting
- **ruff**: Fast Python linter
- **mypy**: Static type checking

#### Configuration

The hooks are configured in `.pre-commit-config.yaml` and use the following tools with their respective configurations:

- **black**: 100 character line length
- **isort**: Black-compatible profile
- **ruff**: Comprehensive linting rules
- **mypy**: Strict type checking 